from __future__ import print_function, with_statement

import os
import shutil
import requests
import six
from bs4 import BeautifulSoup
from b3get.utils import tmp_location, size_of_content, serial_download_file
from io import BytesIO

main_url = "https://data.broadinstitute.org/bbbc/image_sets.html"


def test_b3_unavailable():
    url = main_url.replace('bbb', 'ccc')
    r = requests.get(url)
    assert not r.ok


def test_b3_available():
    r = requests.get(main_url)
    assert r.ok


def test_b3_ds006():
    url = "https://data.broadinstitute.org/bbbc/BBBC006/"
    r = requests.get(url)
    assert r.ok
    assert r.content
    assert r.headers


def test_check_ds006_title():
    url = "https://data.broadinstitute.org/bbbc/BBBC006/"
    r = requests.get(url)
    assert r.ok
    soup = BeautifulSoup(r.text, 'html.parser')
    assert soup.title.string
    print(soup.title.string)


def test_download_ds006_to_tmp():
    url = "https://data.broadinstitute.org/bbbc/BBBC008/"
    r = requests.get(url)
    assert r.ok

    zipurl = 'https://data.broadinstitute.org/bbbc/BBBC008/BBBC008_v1_foreground.zip'
    tdir = tmp_location()
    dst = os.path.join(tdir, 'BBBC008')
    if not os.path.isdir(dst):
        os.makedirs(dst)
    r = requests.get(zipurl)
    assert r.ok
    pulled_bytes = BytesIO(r.content)
    dstf = os.path.join(dst, os.path.split(zipurl)[-1])
    with open(dstf, 'wb') as fo:
        fo.write(pulled_bytes.read())

    assert os.path.exists(dstf)
    assert os.path.isfile(dstf)
    assert os.stat(dstf).st_size > 0
    print(dstf)
    shutil.rmtree(dst)


def test_manually_size_of_content():
    url = 'https://data.broadinstitute.org/bbbc/BBBC008/BBBC008_v1_foreground.zip'
    r = requests.head(url)
    assert r.ok
    assert r.headers
    if six.PY2:
        assert "content-length" in [item.lower() for item in r.headers.keys()]
    else:
        assert "content-length" in r.headers.keys()
    assert r.headers.get("content-length")
    assert int(r.headers.get("content-length")) > 0
    assert int(r.headers.get("content-length")) == 484995


def test_size_of_content():
    nbytes = size_of_content('https://data.broadinstitute.org/bbbc/BBBC008/BBBC008_v1_foreground.zipa')
    assert nbytes == 0
    nbytes = size_of_content('https://data.broadinstitute.org/bbbc/BBBC008/BBBC008_v1_foreground.zip')
    assert nbytes > 0
    assert nbytes == 484995


def test_download_file():
    tmpdir = tmp_location()
    fpath = serial_download_file('https://data.broadinstitute.org/bbbc/BBBC008/BBBC008_v1_foreground.zip', tmpdir)
    assert fpath
    assert os.path.isfile(fpath)
    assert os.stat(fpath).st_size > 0
    assert os.stat(fpath).st_size == 484995
    shutil.rmtree(tmpdir)
