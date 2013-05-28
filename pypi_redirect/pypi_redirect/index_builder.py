def build(package_path, index_rows):
    html_rows = '\n'.join(
        '\n'.join(_rows_for_file(p, r)) for p, r in index_rows.iteritems())
    built = (
        '<html><head><title>Links for {package_name}</title></head>'
        '<body><h1>Links for {package_name}</h1>\n'
        '{html_rows}\n'
        '</body></html>'.format(
            package_name=package_path,
            html_rows=html_rows))
    return built


def _rows_for_file(package_file, row):
    yield _format_row(package_file)
    if row.checksums.md5:
        yield _format_row(package_file + '.md5')
    if row.checksums.sha1:
        yield _format_row(package_file + '.sha1')


def _format_row(filename):
    return '<a href="{f}">{f}</a><br/>'.format(f=filename)