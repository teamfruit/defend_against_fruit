from collections import OrderedDict
from nose.tools import eq_
from pypi_redirect import index_builder
from _test_utils import read_index
from pypi_redirect.index_parser import IndexRow, Checksums


def typical_index_test():
    index_rows = OrderedDict([
        ('Sphinx-0.6.4-py2.5.egg',
            IndexRow(
                download_url=(
                    'https://pypi.python.org/simple/Sphinx/'
                    '../../packages/2.5/S/Sphinx/Sphinx-0.6.4-py2.5.egg'
                    '#md5=b9e637ba15a27b31b7f94b8809cdebe3'),
                checksums=Checksums(
                    md5='b9e637ba15a27b31b7f94b8809cdebe3',
                    sha1=None))),
        ('Sphinx-0.1.61843.tar.gz',
            IndexRow(
                download_url=(
                    'http://pypi.acme.com/packages/source/S/Sphinx/'
                    'Sphinx-0.1.61843.tar.gz'),
                checksums=Checksums(
                    md5=None,
                    sha1=None))),
        ('Sphinx-0.6.5-py2.6.egg',
            IndexRow(
                download_url=(
                    'https://pypi.python.org/simple/Sphinx/'
                    '../../packages/2.6/S/Sphinx/'
                    'Sphinx-0.6.5-py2.6.egg'),
                checksums=Checksums(
                    md5=None,
                    sha1=None))),
        ('Sphinx-0.6b1-py2.5.egg',
            IndexRow(
                download_url=(
                    'https://pypi.python.org/simple/Sphinx/'
                    '../../packages/2.5/S/Sphinx/'
                    'Sphinx-0.6b1-py2.5.egg'
                    '#md5=b877f156e5c4b22257c47873021da3d2'),
                checksums=Checksums(
                    md5='b877f156e5c4b22257c47873021da3d2',
                    sha1=None))),
        ('Sphinx-0.1.61945-py2.5.egg',
            IndexRow(
                download_url=(
                    'https://pypi.python.org/simple/Sphinx/'
                    '../../packages/2.5/S/Sphinx/'
                    'Sphinx-0.1.61945-py2.5.egg'
                    '#md5=8139b5a66e41202b362bac270eef26ad'),
                checksums=Checksums(
                    md5='8139b5a66e41202b362bac270eef26ad',
                    sha1=None))),
        ('Sphinx-0.6-py2.5.egg',
            IndexRow(
                download_url=(
                    'https://pypi.python.org/simple/Sphinx/'
                    '../../packages/2.5/S/Sphinx/'
                    'Sphinx-0.6-py2.5.egg'
                    '#sha1=0000e1d327ab9524a006179aef4155a0d7a0'),
                checksums=Checksums(
                    md5=None,
                    sha1='0000e1d327ab9524a006179aef4155a0d7a0'))),
        ('Sphinx-1.0b2.tar.gz',
            IndexRow(
                download_url=(
                    'https://pypi.python.org/simple/Sphinx/'
                    '../../packages/source/S/Sphinx/'
                    'Sphinx-1.0b2.tar.gz'
                    '#sha1=00006bf13da4fd0542cc85705d1c4abd3c0a'),
                checksums=Checksums(
                    md5=None,
                    sha1='00006bf13da4fd0542cc85705d1c4abd3c0a'))),
        ('Sphinx-0.6.1-py2.4.egg',
            IndexRow(
                download_url=(
                    'http://pypi.acme.com/packages/2.4/S/Sphinx/'
                    'Sphinx-0.6.1-py2.4.egg'
                    '#md5=8b5d93be6d4f76e1c3d8c3197f84526f'),
                checksums=Checksums(
                    md5='8b5d93be6d4f76e1c3d8c3197f84526f',
                    sha1=None))),
        ('Sphinx-0.5.tar.gz',
            IndexRow(
                download_url=(
                    'https://pypi.python.org/simple/Sphinx/'
                    '../../packages/source/S/Sphinx/'
                    'Sphinx-0.5.tar.gz'
                    '#md5=55a33cc13b5096c8763cd4a933b30ddc'),
                checksums=Checksums(
                    md5='55a33cc13b5096c8763cd4a933b30ddc',
                    sha1=None))),
        ('subdir/', None),
    ])

    _assert_parse_results(
        package_path='Sphinx',
        index_rows=index_rows,
        output_file='typical_index_rebuilt.html')


def single_index_test():
    index_rows = OrderedDict([
        ('Sphinx-0.1.61843.tar.gz',
            IndexRow(
                download_url=(
                    'https://pypi.python.org/simple/Sphinx/'
                    '../../packages/source/S/Sphinx/'
                    'Sphinx-0.1.61843.tar.gz'
                    '#md5=69ab7befe60af790d24e22b4b46e8392'),
                checksums=Checksums(
                    md5='69ab7befe60af790d24e22b4b46e8392',
                    sha1=None)))])

    _assert_parse_results(
        package_path='Sphinx',
        index_rows=index_rows,
        output_file='single_index_rebuilt.html')


def empty_index_test():
    _assert_parse_results(
        package_path='Sphinx',
        index_rows=OrderedDict(),
        output_file='empty_index_rebuilt.html')


def directory_index_test():
    index_rows = OrderedDict([
        ('Sphinx/', None),
        ('nose/', None)])

    _assert_parse_results(
        package_path='Python/',
        index_rows=index_rows,
        output_file='directory_index_rebuilt.html')


def _assert_parse_results(package_path, index_rows, output_file):
    actual_html_str = index_builder.build(
        package_path=package_path,
        index_rows=index_rows)

    expected_html_str = read_index(output_file)

    eq_(actual_html_str, expected_html_str)
