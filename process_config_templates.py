import argparse
from collections import namedtuple
import os
from string import Template
import sys
import textwrap


_OPTION_NAMES = ('pypi_server_base', 'pypi_push_username', 'pypi_push_password')


def _slurp_template_file(template_file):
    if not os.path.exists(template_file):
        raise IOError("config template file: {} doesn't exist".format(template_file))
    with open(template_file, 'r') as f:
        whole_template = f.read()
    return whole_template


def _write_output_file(output_file, file_contents):
    with open(output_file, "w") as f:
        f.write(file_contents)


def _process_template(template_file, output_file, parsed_args):
    template_str = _slurp_template_file(template_file)

    template = Template(template_str)
    post_substitute = template.substitute(
        pypi_server_base=parsed_args.pypi_server_base,
        pypi_push_username=parsed_args.pypi_push_username,
        pypi_push_password=parsed_args.pypi_push_password
    )

    _write_output_file(output_file=output_file, file_contents=post_substitute)


def _process_ci_config_dir(relative_ci_config_dir_path, parsed_args):
    base_path = os.path.dirname(os.path.abspath(__file__))

    template_file_name = "virtualenv_util.cfg.template"
    output_file_name = "virtualenv_util.cfg"

    template_file = os.path.join(base_path, relative_ci_config_dir_path, template_file_name)

    output_file = os.path.join(base_path, relative_ci_config_dir_path, output_file_name)

    _process_template(
        template_file=template_file,
        output_file=output_file,
        parsed_args=parsed_args)


EnvTemplateValues = namedtuple('EnvTemplateValues', _OPTION_NAMES)


def _read_environment_for_defaults():
    pypi_server_base_env = os.environ.get('pypi_server_base'.upper(), None)
    pypi_push_username_env = os.environ.get('pypi_push_username'.upper(), None)
    pypi_push_password_env = os.environ.get('pypi_push_password'.upper(), None)

    return EnvTemplateValues(
        pypi_server_base=pypi_server_base_env,
        pypi_push_username=pypi_push_username_env,
        pypi_push_password=pypi_push_password_env)


def _log_values(parsed_args):
    def print_option_value(option, option_value):
        print('{}: {}'.format(option, option_value))

    def log_option_value(option):
        print_option_value(option, getattr(parsed_args, option, None))

    for option in ('pypi_server_base', 'pypi_push_username'):
        log_option_value(option)

    #Avoid printing password in plain text, but still log if there is a None value
    password_value = getattr(parsed_args, 'pypi_push_password', None)
    if password_value:
        print_option_value('pypi_push_password', 'XXXXX')
    else:
        print_option_value('pypi_push_password', 'None')


def _parse_and_validate(parser, command_line_args):
    env_template_values = _read_environment_for_defaults()

    parsed_args = parser.parse_args(command_line_args)

    def handle_arg(key_name):
        opt_value = getattr(parsed_args, key_name, None)
        if not opt_value:
            opt_value = getattr(env_template_values, key_name, None)

        if not opt_value:
            msg = (
                "Error: {key_name} value must be provided.\n\n"
                "This can be done using the relevant command line argument\n"
                "or the corresponding environment variable: {env_name}\n\n{usage}".format(
                    key_name=key_name,
                    env_name=key_name.upper(),
                    usage=parser.format_usage()))
            print msg
            sys.exit(1)

        setattr(parsed_args, key_name, opt_value)

    for key_name in _OPTION_NAMES:
        handle_arg(key_name=key_name)

    return parsed_args


def _parse_args(args=None):
    parser = argparse.ArgumentParser(
        description='Configuration pre-processing tool.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''
           Typical usage of the defend_against_fruit package would not
           use a configuration template processor such as this one,
           but would instead use hard-coded configuration files.

           Since this code is being shared on Github, its configuration
           files must avoid installation specific values.

           It is expected that your CI job will run this substitution
           before executing "ci --publish". A typical build config
           would be:

           Step 1: python process_config_templates.py \\
                      --pypi_server_base=http://myartifactory.defendagainstfruit.com:8081/artifactory \\
                      --pypi_push_username=admin \\
                      --pypi_push_password=password

           Step 2: ci --publish'''))

    parser.add_argument(
        '--pypi-server-base',
        help='Base URL of the Artifactory repository manager')

    parser.add_argument(
        '--pypi-push-username',
        help='Username to be used when pushing to the Artifactory hosted PyPI server.')

    parser.add_argument(
        '--pypi-push-password',
        help='Password to be used when pushing to the Artifactory hosted PyPI server.')

    parsed_args = _parse_and_validate(parser=parser, command_line_args=args)

    return parsed_args


def run(command_line_args):
    parsed_args = _parse_args(command_line_args)
    _log_values(parsed_args)

    _process_ci_config_dir(
        relative_ci_config_dir_path=os.path.join('defend_against_fruit', 'ci_config'),
        parsed_args=parsed_args)

    _process_ci_config_dir(
        relative_ci_config_dir_path=os.path.join('examples', 'daf_basket', 'ci_config'),
        parsed_args=parsed_args)

    _process_ci_config_dir(
        relative_ci_config_dir_path=os.path.join('examples', 'daf_fruit', 'ci_config'),
        parsed_args=parsed_args)

    _process_ci_config_dir(
        relative_ci_config_dir_path=os.path.join('examples', 'daf_pest', 'ci_config'),
        parsed_args=parsed_args)

    _process_ci_config_dir(
        relative_ci_config_dir_path=os.path.join('pypi_redirect', 'ci_config'),
        parsed_args=parsed_args)


if __name__ == '__main__':
    command_line_args = sys.argv[1:]
    run(command_line_args)
