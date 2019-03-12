from __future__ import print_function, with_statement

import tempfile
import os
import re
import requests
import tqdm


def tmp_location():
    """ return a folder under /tmp or similar,
    If something exists that matches the name '.*-b3get', use this.
    If nothing is found, a new folder under /tmp is created and returned
    """
    tmp = tempfile.gettempdir()
    folders = [subdir[0] for subdir in os.walk(tmp) if subdir[0].endswith('-b3get')]
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
    try:
        r = requests.head(url, timeout=2)
    except requests.exceptions.Timeout as texc:
        print('timed out on',url,texc)
        return 0
    except Exception as ex:
        raise ex

    value = 0
    if not r.ok:
        print('E url {} does not exist'.format(url))
        return value

    value = int(r.headers.get('content-length'))
    return value


def serial_download_file(url, dstfolder, chunk_bytes=1024*1024, npos=None):
    """ download file from <url> into folder <dstfolder>
    returns the full path of the successfully downloaded file
    """

    if not os.path.exists(dstfolder):
        print('E destination path {} does not exist'.format(dstfolder))
        return ""
    r = requests.get(url, stream=True, timeout=2)
    assert r.ok, "unable to access URL: {}".format(url)
    _, fname = os.path.split(url)
    dstf = os.path.join(dstfolder, fname)
    total_length = int(r.headers.get('content-length'))

    if os.path.isfile(dstf) and os.stat(dstf).st_size == total_length:  # nothing to download
        return dstf
    with open(dstf, 'wb') as fo:

        if total_length == 0:  # no content length header
            fo.write(r.content)
        else:
            total_length = int(total_length)
            nbytes = 0
            pbar = None
            if not npos:
                pbar = tqdm.tqdm(total=total_length, unit='B', unit_scale=True)
            else:
                pbar = tqdm.tqdm(total=total_length, unit='B', unit_scale=True, position=npos)

            for data in r.iter_content(chunk_size=chunk_bytes):
                fo.write(data)
                pbar.update(len(data))
                nbytes += len(data)

    return dstf


def wrap_serial_download_file(args):
    return serial_download_file(*args)
