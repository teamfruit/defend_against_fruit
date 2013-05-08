import cherrypy
from simple import Simple


def run_server():
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

    class Root(object):
        """
        Requests to the server root should do nothing.
        """
        pass

    root = Root()
    root.python = Simple()
    cherrypy.quickstart(root)


if __name__ == '__main__':
    run_server()
