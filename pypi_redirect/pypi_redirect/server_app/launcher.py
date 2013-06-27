from logging import handlers, DEBUG
import logging
import os
import shutil
import sys
import cherrypy
from dependency_injection import wire_dependencies


def run_server(primordial_logger=None, enable_file_logging=False):
    """
    Run the server which proxies requests from:
        python/<package>
    to:
        https://pypi.python.org/simple/<package>

    And requests from:
        python/<package>/<filename>
    to:
        https://pypi.python.org/<path-to-filename>
    """
    if primordial_logger is None:
        primordial_logger = _create_console_logger()

    root = wire_dependencies()

    cherrypy_config_path = _get_cherrypy_config_file(primordial_logger)

    app = cherrypy.tree.mount(
        root,
        script_name='/',
        config=cherrypy_config_path)

    cherrypy.config.update(cherrypy_config_path)

    if enable_file_logging:
        _enable_file_logging(app, primordial_logger=primordial_logger)

    cherrypy.engine.start()
    cherrypy.engine.block()


def _get_cherrypy_config_file(primordial_logger):
    cherrypy_config_path = _config_path('pypi_redirect.conf')

    if not os.path.exists(cherrypy_config_path):
        template_path = _config_path('pypi_redirect.conf.template')

        assert os.path.exists(template_path), \
            'Neither the CherryPy config file ("{}") nor a suitable ' \
            'template ("{}") were found.'.format(
                cherrypy_config_path,
                template_path)

        shutil.copyfile(template_path, cherrypy_config_path)

        primordial_logger.info(
            'Created CherryPy config file "{}" from template "{}"'.format(
                cherrypy_config_path,
                template_path))

    primordial_logger.info(
        'Using CherryPy config file "{}"'.format(cherrypy_config_path))

    return cherrypy_config_path


def _sys_prefix_path(*path):
    return os.path.join(sys.prefix, 'pypi_redirect', *path)


def _config_path(*path):
    return _sys_prefix_path('config', *path)


def _log_path(*path):
    return _sys_prefix_path('log', *path)


def _abs_log_path(log_filename):
    if not os.path.isabs(log_filename):
        return _log_path(log_filename)
    else:
        return log_filename


def _ensure_path_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def _enable_file_logging(app, primordial_logger):
    # Remove the default FileHandlers if present.
    app.log.error_file = ""
    app.log.access_file = ""

    _add_handler(
        app=app,
        logger=app.log.error_log,
        log_filename_config_attr='rot_error_file',
        log_filename_default_value='error.log',
        max_bytes_config_attr='rot_error_maxBytes',
        backup_count_config_attr='rot_error_backupCount',
        primordial_logger=primordial_logger)

    _add_handler(
        app=app,
        logger=app.log.access_log,
        log_filename_config_attr='rot_access_file',
        log_filename_default_value='access.log',
        max_bytes_config_attr='rot_access_maxBytes',
        backup_count_config_attr='rot_access_backupCount',
        primordial_logger=primordial_logger)


def _add_handler(
        app,
        logger,
        log_filename_config_attr,
        log_filename_default_value,
        max_bytes_config_attr,
        backup_count_config_attr,
        primordial_logger):

    def get_attr_and_log_value(attr, default_value):
        value = getattr(app.log, attr, default_value)
        primordial_logger.info(
            'log.{}: {!r} (default {!r})'.format(attr, value, default_value))
        return value

    max_bytes = get_attr_and_log_value(max_bytes_config_attr, 1000000)
    backup_count = get_attr_and_log_value(backup_count_config_attr, 4)
    fname = get_attr_and_log_value(
        log_filename_config_attr,
        log_filename_default_value)

    fname = _abs_log_path(fname)

    primordial_logger.info(
        'log.{} as abs path: {!r}'.format(log_filename_config_attr, fname))

    _ensure_path_exists(os.path.dirname(fname))

    h = handlers.RotatingFileHandler(fname, 'a', max_bytes, backup_count)
    h.setLevel(DEBUG)
    h.setFormatter(cherrypy._cplogging.logfmt)

    logger.addHandler(h)


def _create_console_logger():
    console_logger = logging.getLogger('PyPIRedirect')
    console_logger.setLevel(DEBUG)

    h = logging.StreamHandler()
    console_logger.addHandler(h)
    return console_logger
