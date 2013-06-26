from logging import handlers, DEBUG
import logging
import cherrypy
import win32serviceutil
import win32service
from ..server_app.launcher import run_server


class PyPIWindowsService(win32serviceutil.ServiceFramework):
    """NT Service."""
    _svc_name_ = "PyPIRedirectService"
    _svc_display_name_ = "PyPI Redirect Service"

    def SvcDoRun(self):
        svc_logger = _create_svc_logger()
        run_server(primordial_logger=svc_logger, enable_file_logging=True)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        cherrypy.engine.exit()

        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        # very important for use with py2exe
        # otherwise the Service Controller never knows that it is stopped !


def _create_svc_logger():
    svc_logger = logging.getLogger(PyPIWindowsService._svc_name_)
    svc_logger.setLevel(DEBUG)

    h = handlers.NTEventLogHandler(PyPIWindowsService._svc_display_name_)
    svc_logger.addHandler(h)
    return svc_logger


def main():
    win32serviceutil.HandleCommandLine(PyPIWindowsService)


if __name__ == '__main__':
    main()
