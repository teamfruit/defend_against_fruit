from collections import namedtuple, OrderedDict
from lxml import etree
import urlparse


Checksums = namedtuple('Checksums', ('md5', 'sha1'))
IndexRow = namedtuple('IndexRow', ('download_url', 'checksums'))


def _all_internal_links_and_directories(html_root):
    return html_root.xpath(
        ".//a["
        "  @rel = 'internal'"
        "  or "
        "  ("
        "    substring(@href, 1, string-length(text())) = text()"
        "    and "
        "    substring(@href, string-length(@href)) = '/'"
        "  )"
        "]")


def parse(
        base_url,
        package_path,
        html_str,
        strict_html=True,
        find_links_fn=_all_internal_links_and_directories):
    html_root = _parse_html(html_str, strict_html)
    rows = _parse_internal_links(
        base_url,
        html_root,
        package_path,
        find_links_fn)
    return rows


def _parse_internal_links(base_url, html_root, package_path, find_links_fn):
    rows = OrderedDict()
    for link in find_links_fn(html_root):
        href = link.attrib['href']
        if not _is_ascii(href):
            continue
        if href.endswith('/'):
            if not _is_absolute_url(href):
                rows[href] = None
        else:
            rows[link.text.strip()] = IndexRow(
                download_url=_make_url_absolute(base_url, package_path, href),
                checksums=_determine_checksums(href))
    return rows


def _is_ascii(s):
    try:
        s.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False


def _parse_html(html_str, strict_html):
    parser = etree.HTMLParser(recover=not strict_html)
    html_root = etree.fromstring(html_str, parser)
    return html_root


def _is_absolute_url(url):
    return bool(urlparse.urlparse(url).scheme)


def _make_url_absolute(base_url, package_path, url):
    if _is_absolute_url(url):
        return url
    return '{}/{}/{}'.format(base_url, package_path, url)


def _determine_checksums(href):
    split_url = urlparse.urlsplit(href)
    fragment = split_url.fragment
    fragment_dict = dict((fragment.split('='),)) if fragment else {}

    checksums = Checksums(
        md5=fragment_dict.get('md5', None),
        sha1=fragment_dict.get('sha1', None))

    return checksums
