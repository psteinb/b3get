import os
import shutil
import requests
from bs4 import BeautifulSoup
from b3get.utils import tmp_location
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
    url = "https://data.broadinstitute.org/bbbc/BBBC006/"
    r = requests.get(url)
    assert r.ok

    zipurl = 'https://data.broadinstitute.org/bbbc/BBBC006/BBBC006_v1_labels.zip'
    tdir = tmp_location()
    dst = os.path.join(tdir, 'BBBC006')
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
