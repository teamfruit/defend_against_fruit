from nose.tools import eq_
from pypi_redirect import index_builder
from pypi_redirect import index_parser
from _test_utils import read_index


def typical_index_test():
    _assert_parse_results(
        input_file='typical_index.html',
        output_file='typical_index_rebuilt.html')


def single_index_test():
    _assert_parse_results(
        input_file='single_index.html',
        output_file='single_index_rebuilt.html')


def empty_index_test():
    _assert_parse_results(
        input_file='empty_index.html',
        output_file='empty_index_rebuilt.html')


def _assert_parse_results(input_file, output_file):
    original_html_str = read_index(input_file)

    index_rows = index_parser.parse(
        base_url='https://pypi.python.org/simple',
        package_path='Sphinx',
        html_str=original_html_str)

    actual_html_str = index_builder.build(
        package_path='Sphinx',
        index_rows=index_rows)

    expected_html_str = read_index(output_file)

    eq_(actual_html_str, expected_html_str)
