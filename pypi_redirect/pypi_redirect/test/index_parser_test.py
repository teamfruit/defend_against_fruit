from collections import OrderedDict
from nose.tools import eq_, raises
from pypi_redirect import index_parser
from lxml.etree import XMLSyntaxError
from _utils import read_index


def typical_index_test():
    expected = OrderedDict((
        ('Sphinx-0.6.4-py2.5.egg', index_parser.IndexRow(
            download_url='https://pypi.python.org/simple/Sphinx/../../packages'
                         '/2.5/S/Sphinx/Sphinx-0.6.4-py2.5.egg'
                         '#md5=b9e637ba15a27b31b7f94b8809cdebe3',
            checksums=index_parser.Checksums(
                md5='b9e637ba15a27b31b7f94b8809cdebe3',
                sha1=None))),
        ('Sphinx-0.1.61843.tar.gz', index_parser.IndexRow(
            download_url='http://pypi.acme.com/packages'
                         '/source/S/Sphinx/Sphinx-0.1.61843.tar.gz',
            checksums=index_parser.Checksums(
                md5=None,
                sha1=None))),
        ('Sphinx-0.6.5-py2.6.egg', index_parser.IndexRow(
            download_url='https://pypi.python.org/simple/Sphinx/../../packages'
                         '/2.6/S/Sphinx/Sphinx-0.6.5-py2.6.egg',
            checksums=index_parser.Checksums(
                md5=None,
                sha1=None))),
        ('Sphinx-0.6b1-py2.5.egg', index_parser.IndexRow(
            download_url='https://pypi.python.org/simple/Sphinx/../../packages'
                         '/2.5/S/Sphinx/Sphinx-0.6b1-py2.5.egg'
                         '#md5=b877f156e5c4b22257c47873021da3d2',
            checksums=index_parser.Checksums(
                md5='b877f156e5c4b22257c47873021da3d2',
                sha1=None))),
        ('Sphinx-0.1.61945-py2.5.egg', index_parser.IndexRow(
            download_url='https://pypi.python.org/simple/Sphinx/../../packages'
                         '/2.5/S/Sphinx/Sphinx-0.1.61945-py2.5.egg'
                         '#md5=8139b5a66e41202b362bac270eef26ad',
            checksums=index_parser.Checksums(
                md5='8139b5a66e41202b362bac270eef26ad',
                sha1=None))),
        ('Sphinx-0.6-py2.5.egg', index_parser.IndexRow(
            download_url='https://pypi.python.org/simple/Sphinx/../../packages'
                         '/2.5/S/Sphinx/Sphinx-0.6-py2.5.egg'
                         '#sha1=0000e1d327ab9524a006179aef4155a0d7a0',
            checksums=index_parser.Checksums(
                md5=None,
                sha1='0000e1d327ab9524a006179aef4155a0d7a0'))),
        ('Sphinx-1.0b2.tar.gz', index_parser.IndexRow(
            download_url='https://pypi.python.org/simple/Sphinx/../../packages'
                         '/source/S/Sphinx/Sphinx-1.0b2.tar.gz'
                         '#sha1=00006bf13da4fd0542cc85705d1c4abd3c0a',
            checksums=index_parser.Checksums(
                md5=None,
                sha1='00006bf13da4fd0542cc85705d1c4abd3c0a'))),
        ('Sphinx-0.6.1-py2.4.egg', index_parser.IndexRow(
            download_url='http://pypi.acme.com/packages'
                         '/2.4/S/Sphinx/Sphinx-0.6.1-py2.4.egg'
                         '#md5=8b5d93be6d4f76e1c3d8c3197f84526f',
            checksums=index_parser.Checksums(
                md5='8b5d93be6d4f76e1c3d8c3197f84526f',
                sha1=None))),
        ('Sphinx-0.5.tar.gz', index_parser.IndexRow(
            download_url='https://pypi.python.org/simple/Sphinx/../../packages'
                         '/source/S/Sphinx/Sphinx-0.5.tar.gz'
                         '#md5=55a33cc13b5096c8763cd4a933b30ddc',
            checksums=index_parser.Checksums(
                md5='55a33cc13b5096c8763cd4a933b30ddc',
                sha1=None))),
        ('subdir/', None)
    ))
    _assert_parse_results('typical_index.html', expected)


def single_index_test():
    expected = OrderedDict((
        ('Sphinx-0.1.61843.tar.gz', index_parser.IndexRow(
            download_url='https://pypi.python.org/simple/Sphinx/../../packages'
                         '/source/S/Sphinx/Sphinx-0.1.61843.tar.gz'
                         '#md5=69ab7befe60af790d24e22b4b46e8392',
            checksums=index_parser.Checksums(
                md5='69ab7befe60af790d24e22b4b46e8392',
                sha1=None))),
    ))
    _assert_parse_results('single_index.html', expected)


def empty_index_test():
    expected = OrderedDict()
    _assert_parse_results('empty_index.html', expected)


def directory_index_test():
    expected = OrderedDict((
        ('Sphinx/', None),
        ('nose/', None),
    ))
    _assert_parse_results('directory_index.html', expected)


@raises(XMLSyntaxError)
def bad_index_test():
    _assert_parse_results('bad_index.html')


def _assert_parse_results(index_filename, expected=None):
    html_str = read_index(index_filename)
    actual = index_parser.parse(
        base_url='https://pypi.python.org/simple',
        package_path='Sphinx',
        html_str=html_str)
    eq_(actual, expected)
