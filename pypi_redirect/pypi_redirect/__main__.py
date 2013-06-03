import cherrypy
import http


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
    cherrypy.quickstart(http.wire())


if __name__ == '__main__':
    run_server()
