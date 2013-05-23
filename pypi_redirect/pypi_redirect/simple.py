
# NOTE: This is a prototype. We will be completely rewriting and thoroughly
# testing it.

import urlparse
import cherrypy
import requests
from lxml import etree


# TODO: / => fake listing with "python" directory
# /python => 301 redirects to /python/
# TODO: /python/ => fake listing with all PyPI packages
# /python/Sphinx => 301 redirects to /python/Sphinx/
# /python/Sphinx/ => fake listing with all Sphinx packages
# TODO: /python/sphinx => 301 redirects to /python/Sphinx/
# TODO: /python/sphinx/ => 301 redirects to /python/Sphinx/
# /python/Sphinx/Sphinx-1.0.6.tar.gz => 302 redirect to actual Sphinx package
# TODO: /python/Sphinx/Sphinx-1.0.6.tar.gz.md5 => returns file containing MD5
# TODO: /python/Sphinx/Sphinx-1.0.6.tar.gz.sha1 => 404

#   1. Disable automatic checksums in Artifactory.
#   2. Clear repo cache.
#   3. In a browser, request a package.
#   4. Where did Artifactory look for the MD5? Original URL or the redirect?
#
#   Best testing option: Ignore and pass-through
#   Best 'real' option: Generate if absent [default]

# Lessons:
#   - 302 redirect for artifact works fine
#   - Checksum returns to the original URL (plus .md5), not the redirected one
#   - Consequence: no streaming required (for this Artifactory version)


class Simple(object):
    def __init__(
            self,
            base_url='https://pypi.python.org/simple',
            http_get_fn=requests.get):
        self.base_url = base_url
        self.http_get_fn = http_get_fn

    @cherrypy.expose
    def default(self, *path):
        if not path:
            return self.http_get_fn(self.base_url).text

        pypi_dir_url = '{}/{}'.format(self.base_url, path[0])
        html_root = self.__get_dir_html(pypi_dir_url)

        if len(path) == 1:
            if not cherrypy.request.is_index:
                raise cherrypy.HTTPRedirect(cherrypy.url() + '/', 301)

            return self.__get_package_dir(
                package_dir=path[0],
                html_root=html_root)

        elif len(path) == 2:
            if path[-1].lower().endswith('.md5'):
                return self.__get_md5_file(
                    package_dir_url=pypi_dir_url,
                    package_file=path[1][:-4],
                    html_root=html_root)
            else:
                return self.__get_package_file(
                    package_dir_url=pypi_dir_url,
                    package_file=path[1],
                    html_root=html_root)

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
            raise cherrypy.HTTPRedirect(package_path, 302)
        raise cherrypy.NotFound()

    def __get_md5_file(self, package_dir_url, package_file, html_root):
        for link in html_root.xpath(".//a[text()='{}']".format(package_file)):
            split_url = urlparse.urlsplit(link.attrib['href'])
            md5 = split_url.fragment.split('=')[-1]
            if not md5:
                raise cherrypy.NotFound('MD5 hash not available')
            cherrypy.response.headers['Content-Type'] = \
                'application/x-checksum'
            return md5

    def __assign_headers(self, headers):
        for k, v in headers.iteritems():
            cherrypy.response.headers[k] = v