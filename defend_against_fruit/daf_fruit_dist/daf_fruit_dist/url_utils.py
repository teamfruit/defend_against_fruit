def subtract_index_url(index_url, pkg_url):
    """Subtract index_url from pkg_url and return remainder."""
    found_index = pkg_url.find(index_url)

    if found_index != 0:
        raise RuntimeError(
            "pkg_url of {pkg_url} does not start with index_url of "
            "{index_url}".format(
                index_url=index_url,
                pkg_url=pkg_url))
    else:
        tail = pkg_url[len(index_url):]

    stripped_tail = tail.lstrip('/')

    if not stripped_tail:
        raise RuntimeError(
            "pkg_url of {pkg_url} and index_url of {index_url} are "
            "effectively identical.".format(
                index_url=index_url,
                pkg_url=pkg_url))

    return stripped_tail
