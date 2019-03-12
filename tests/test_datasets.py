import os
import requests
import shutil
import zipfile
import glob

from bs4 import BeautifulSoup
from b3get.utils import filter_files, tmp_location
from b3get.datasets import dataset, ds_006, ds_008, ds_024, ds_027
import pytest

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


def test_006_wrong_URL():
    with pytest.raises(RuntimeError):
        ds = dataset(None)

    with pytest.raises(RuntimeError):
        ds = ds_006("https://data.broadinstitute.org/bbbc/BBC027/")


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


def test_008_pull_single():
    ds8 = ds_008()
    imgs = ds8.list_images()
    assert len(imgs) > 0
    few = filter_files(imgs, '.*.zip')
    assert len(few) == 1
    downed = ds8.pull_images('.*.zip')
    assert downed
    assert len(downed) > 0
    assert os.path.exists(downed[0])
    shutil.rmtree(tmp_location())


def test_008_list_gt():
    ds8 = ds_008()
    imgs = ds8.list_gt()
    assert len(imgs) > 0
    assert len(imgs) == 1
    assert "BBBC008_v1_foreground.zip" in imgs
    urls = ds8.list_gt(True)
    assert len(urls) > 0


def test_008_pull_gt():
    ds8 = ds_008()
    imgs = ds8.pull_gt()
    assert len(imgs) > 0
    assert len(imgs) == 1
    assert "BBBC008_v1_foreground.zip" in [os.path.split(item)[-1] for item in imgs]
    shutil.rmtree(tmp_location())


def test_008_extract_gt_manual():
    ds8 = ds_008()
    imgs = ds8.pull_gt()
    assert len(imgs) > 0
    assert len(imgs) == 1
    assert "BBBC008_v1_foreground.zip" in [os.path.split(item)[-1] for item in imgs]
    with zipfile.ZipFile(imgs[0], 'r') as zf:
        print('extracting ',imgs[0])
        zf.extractall(os.path.split(imgs[0])[0])
        zf.close()
    path = os.path.split(imgs[0])[0]
    xpath = os.path.join(path, "human_ht29_colon_cancer_2_foreground")
    assert os.path.exists(xpath)
    assert os.path.isdir(xpath)
    extracted = glob.glob(os.path.join(xpath, "*.tif"))
    assert len(extracted) > 0
    assert len(extracted) == 24  # channel 2 is not contained
    shutil.rmtree(tmp_location())


def test_008_extract_gt():
    shutil.rmtree(tmp_location())
    ds8 = ds_008()
    imgs = ds8.pull_gt()
    assert len(imgs) > 0
    assert len(imgs) == 1
    print(imgs)
    xtracted = ds8.extract_gt()
    assert xtracted
    assert len(xtracted) > 0
    assert len(xtracted) == 24
    shutil.rmtree(tmp_location())


def test_008_images_to_numpy():
    shutil.rmtree(tmp_location())
    ds8 = ds_008()
    imgs = ds8.pull_images()
    assert len(imgs) > 0
    assert len(imgs) == 1
    xtracted = ds8.extract_images()
    assert len(xtracted) == 24
    nplist = ds8.to_numpy(os.path.split(xtracted[0])[0])
    assert nplist
    assert len(nplist) > 0
    assert len(nplist) == 24
    assert nplist[0].shape != tuple()
    assert nplist[0].shape == (512, 512)
    shutil.rmtree(tmp_location())


def test_006_list_gt():
    ds6 = ds_006()
    imgs = ds6.list_gt()
    assert len(imgs) > 0
    assert len(imgs) == 1
    assert "BBBC006_v1_labels.zip" in imgs


def test_024_list():
    ds = ds_024()
    imgs = ds.list_images()
    assert len(imgs) > 0
    gt = ds.list_gt()
    assert len(gt) > 0
