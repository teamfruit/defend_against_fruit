import cherrypy
import requests
from lxml import etree


class Simple(object):
    def __init__(self, base_url='https://pypi.python.org/simple', http_get_fn=requests.get):
        self.base_url = base_url
        self.http_get_fn = http_get_fn

    @cherrypy.expose
    def default(self, *path):
        if not path:
            return self.http_get_fn(self.base_url).text

        pypi_dir_url = '{}/{}'.format(self.base_url, path[0])
        html_root = self.__get_dir_html(pypi_dir_url)

        if len(path) == 1:
            return self.__get_package_dir(package_dir=path[0], html_root=html_root)

        elif len(path) == 2:
            return self.__get_package_file(package_dir_url=pypi_dir_url, package_file=path[1], html_root=html_root)

    def __get_dir_html(self, pypi_dir):
        response = self.http_get_fn(pypi_dir)
        parser = etree.HTMLParser()
        html_root = etree.fromstring(response.text, parser)
        return html_root

    def __get_package_dir(self, package_dir, html_root):
        for link in html_root.xpath('.//a'):
            if link.text.lower().startswith(package_dir.lower()):
                link.attrib['href'] = link.text.strip()
        return etree.tostring(html_root, pretty_print=False, method='html')

    def __get_package_file(self, package_dir_url, package_file, html_root):
        for link in html_root.xpath(".//a[text()='{}']".format(package_file)):
            package_path = '{}/{}'.format(package_dir_url, link.attrib['href'])
            response = self.http_get_fn(package_path)
            self.__assign_headers(response.headers)
            return response.content

    def __assign_headers(self, headers):
        for k, v in headers.iteritems():
            cherrypy.response.headers[k] = v
