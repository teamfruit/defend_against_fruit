import os
import cherrypy
import requests
from time import sleep
from nose.tools import eq_
from multiprocessing import Process
from pypi_redirect.simple import Simple


def _read_file(relative_path):
    path_dirname = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(path_dirname, *relative_path)) as f:
        return f.read().strip()


class MockResponse(object):
    def __init__(self, text=None, content=None, headers=None):
        self.__text = text or content
        self.__content = content or text
        self.__headers = headers or {}

    @property
    def text(self):
        return self.__text

    @property
    def content(self):
        return self.__content

    @property
    def headers(self):
        return self.__headers


class MockGet(object):
    def __init__(self, dest_base_url, response_map):
        def _convert_path(relative_path):
            """Replace the first directory in the relative path with dest_base_url."""
            return os.path.join(dest_base_url, *os.path.split(relative_path)[1:])
        self.__response_map = {
            _convert_path(path): (response, output) for path, response, output in response_map}
        self.gets = {}

    def __call__(self, url):
        try:
            self.gets[url] += 1
        except KeyError:
            self.gets[url] = 1
        return self.__response_map[url][0]


def foo_test():
    """
    Ensure that Simple GETs the base_url plus requested paths.
    """
    dest_base_url = 'https://non-existent-url.foo/bar'

    response_map = (
        (
            'python/nose',
            MockResponse(text=_read_file(relative_path=('resources', 'nose', 'input.html'))),
            MockResponse(text=_read_file(relative_path=('resources', 'nose', 'output.html')))
        ),
        # (
        #     'python/nose/nose-1.3.0.tar.gz',
        #     MockResponse(content=_read_file(relative_path=('resources', 'nose', 'redirect', 'nose-1.3.0.tar.gz'))),
        #     MockResponse(content=_read_file(relative_path=('resources', 'nose', 'redirect', 'nose-1.3.0.tar.gz')))
        # )
    )

    mock_get = MockGet(dest_base_url, response_map)

    simple = Simple(base_url=dest_base_url, http_get_fn=mock_get)

    with ServerRunning(simple) as server:
        for path, _, desired_response in response_map:
            actual_response = server.get(path)
            eq_(actual_response.text, desired_response.text)
            eq_(actual_response.content, desired_response.content)


server_base_url = 'http://localhost:8080/'


class ServerRunning(object):
    def __init__(self, simple, attempts_on_start=5):
        self.__simple = simple
        self.__attempts_on_start = attempts_on_start

    def get(self, path):
        return requests.get(server_base_url + path)

    def __wait_until_up(self):
        for i in xrange(self.__attempts_on_start):
            try:
                requests.get(server_base_url + 'status')
                break
            except requests.ConnectionError:
                sleep(0.1)
        else:
            # noinspection PyExceptionInherit
            raise requests.ConnectionError(
                'Failed to connect to the server after {} attempts.'.format(
                    self.__attempts_on_start))

    def __shutdown(self):
        try:
            requests.get(server_base_url + 'exit')
        except requests.ConnectionError:
            pass
        self.__process.join()

    def __run_server(self):
        """
        This should be run in a subprocess.
        """
        class Root(object):
            """
            Requests to the server root should do nothing.
            """
            pass

        class Status(object):
            """
            Returns a simple string when the server is ready.
            """
            @cherrypy.expose
            def default(self):
                return 'up'

        class Exit(object):
            """
            Exits the server when /exit is accessed.
            """
            @cherrypy.expose
            def default(self):
                cherrypy.engine.exit()

        root = Root()
        root.exit = Exit()
        root.status = Status()
        root.python = self.__simple
        cherrypy.quickstart(root)

    def __enter__(self):
        self.__process = Process(target=self.__run_server)
        try:
            self.__process.start()
            self.__wait_until_up()
            return self
        except:
            self.__shutdown()
            raise

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__shutdown()
