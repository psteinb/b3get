import os
import requests
from bs4 import BeautifulSoup
from b3get.utils import filter_files
from b3get.datasets import ds_006, ds_027

# manual tests for exploration


def test_006_images_manual():

    r = requests.get("https://data.broadinstitute.org/bbbc/BBBC006/")
    hdoc = BeautifulSoup(r.text, 'html.parser')
    all_links = hdoc.find_all('a')
    values = []
    for anc in all_links:
        href = anc.get('href')
        if len(href) > 0 and "zip" in href and "images" in href:
            values.append(href)

    assert len(values) > 0
    assert len(values) == 34


def test_006_construction():
    ds6 = ds_006("https://data.broadinstitute.org/bbbc/BBBC006/")
    assert ds6.baseurl
    assert 'BBBC006' in ds6.baseurl
    assert ds6.title()
    assert 'Human' in ds6.title()

    ds6_empty = ds_006()
    assert ds6_empty.baseurl
    assert 'BBBC006' in ds6_empty.baseurl
    assert ds6_empty.title()
    assert 'Human' in ds6_empty.title()


def test_027_construction():
    ds27 = ds_027("https://data.broadinstitute.org/bbbc/BBBC027/")
    assert ds27.baseurl
    assert 'BBBC027' in ds27.baseurl
    assert ds27.title()
    assert '3D Colon' in ds27.title()

    ds27_empty = ds_027()
    assert ds27_empty.baseurl
    assert 'BBBC027' in ds27_empty.baseurl
    assert ds27_empty.title()
    assert '3D Colon' in ds27_empty.title()


def test_006_list_images():
    ds6 = ds_006("https://data.broadinstitute.org/bbbc/BBBC006/")
    imgs = ds6.list_images()
    assert len(imgs) > 0
    assert len(imgs) == 34


def test_027_list_images():
    ds = ds_027("https://data.broadinstitute.org/bbbc/BBBC027/")
    imgs = ds.list_images()
    assert len(imgs) > 0
    assert len(imgs) == 6


def test_006_pull_single():
    ds6 = ds_006("https://data.broadinstitute.org/bbbc/BBBC006/")
    imgs = ds6.list_images()
    assert len(imgs) > 0
    few = filter_files(imgs, '.*_17.zip')
    assert len(few) == 1
    downed = ds6.pull_images('.*_17.zip')
    assert downed
    assert len(downed) > 0
    assert os.path.exists(downed[0])
