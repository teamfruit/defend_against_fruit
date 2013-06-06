import cgi


def build(index_rows):
    html_rows = '\n'.join(
        '\n'.join(_rows_for_file(p, r)) for p, r in index_rows.iteritems())
    built = (
        '<html><body>\n'
        '{html_rows}\n'
        '</body></html>'.format(html_rows=html_rows))
    return built


def _rows_for_file(package_filename, index_row):
    yield _format_row(package_filename)
    if index_row:
        if index_row.checksums.md5:
            yield _format_row(package_filename + '.md5')
        if index_row.checksums.sha1:
            yield _format_row(package_filename + '.sha1')


def _format_row(filename):
    return '<a href="{}">{}</a><br/>'.format(
        _escape_for_html(filename, quote=True),
        _escape_for_html(filename))


def _escape_for_html(s, quote=False):
    return cgi.escape(s, quote=quote).encode('ascii', 'xmlcharrefreplace')