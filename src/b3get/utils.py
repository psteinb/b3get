import tempfile
import os
import re
import requests

def tmp_location():
    """ return a folder under /tmp or similar,
    If something exists that matches the name '.*-b3get', use this.
    If nothing is found, a new folder under /tmp is created and returned
    """
    tmp = tempfile.gettempdir()
    folders = [ subdir[0] for subdir in os.walk(tmp) if subdir[0].endswith('-b3get') ]
    if len(folders) > 0:
        return folders[0]
    else:
        return tempfile.mkdtemp(suffix='-b3get')


def filter_files(alist, rex):
    """ given a list (of strings), filter out items that match the regular express rex """
    if not isinstance(rex,str) or len(rex) == 0:
        return alist
    compiled = re.compile(rex)
    srcs = [item for item in alist if compiled.search(item)]
    return srcs


def size_of_content(url):
    """ given an URL, return the number of bytes stored in the header attribute content-length """
    r = requests.get(url)
    value = 0
    if not r.ok:
        return value

    r = requests.head(url)
    assert "content-length" in r.headers.keys()
    value = int(r.headers["content-length"])
    return value
