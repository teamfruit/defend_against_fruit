from _utils import assert_http_not_found
from ..server_app.handler.invalid_path_handler import InvalidPathHandler


def typical_usage_test():
    def handler_runner():
        InvalidPathHandler().handle(
            path=['path', 'little', 'too', 'long'],
            request=None,
            response=None)

    assert_http_not_found(
        run_handler_fn=handler_runner,
        failure_description='Failed to raise 404 on invalid path')