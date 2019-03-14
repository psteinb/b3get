import os
import requests
import shutil
import zipfile
import glob
import tifffile
import numpy as np

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
        ds = dataset("https://data.broadinstitute.org/bbbc/BBC027/")

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
    ds6 = ds_006(datasetid=6)
    imgs = ds6.list_images()
    assert len(imgs) > 0
    assert len(imgs) == 34


def test_006_list_images_from_datasetid():
    ds = dataset(datasetid=14)
    imgs = ds.list_images()
    assert len(imgs) > 0


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
    assert len(xtracted) == 24+1  # +1 for .DS_Store file contained
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


def test_008_extract_images():
    ds = ds_008()
    _ = ds.pull_images()
    ximgs = ds.extract_images()
    assert len(ximgs) > 0
    assert len(ximgs) == 24+3  # +3 for .DS_Store and similar files contained
    shutil.rmtree(ds.tmp_location)


def test_008_extract_images_nprocs2():
    ds = ds_008()
    _ = ds.pull_images()
    ximgs = ds.extract_images(folder=None, nprocs=2)
    assert len(ximgs) > 0
    assert len(ximgs) == 24+3  # +3 for .DS_Store and similar files contained
    shutil.rmtree(ds.tmp_location)


def test_008_extract_gt_nprocs2():
    ds = ds_008()
    _ = ds.pull_gt()
    ximgs = ds.extract_gt(folder=None, nprocs=2)
    assert len(ximgs) > 0
    assert len(ximgs) == 24+1  # +1 for .DS_Store file contained
    shutil.rmtree(ds.tmp_location)


def test_008_files_to_numpy():
    ds = ds_008()
    _ = ds.pull_images()
    ximgs = ds.extract_images()
    assert len(ximgs) > 0
    assert len(ximgs) == 24+3  # +3 for .DS_Store and similar files contained

    ximgs = [item for item in ximgs if item.count('.tif')]
    first = tifffile.imread(ximgs[0])
    last = tifffile.imread(ximgs[-1])

    npimgs = ds.files_to_numpy(ximgs)
    assert len(npimgs) == len(ximgs)
    assert npimgs[0].shape == first.shape
    assert isinstance(npimgs[0], np.ndarray)
    assert np.array_equal(npimgs[0][:100], first[:100])
    assert np.array_equal(npimgs[-1][:100], last[:100])
    assert npimgs[0].shape == (512, 512)
    shutil.rmtree(ds.tmp_location)


def test_008_ds_images_to_numpy():
    ds = ds_008()
    imgs = ds.images_to_numpy()
    assert len(imgs) > 0
    assert len(imgs) == 24
    assert np.all([item.shape == (512, 512) for item in imgs])

    imgs_plus_fnames = ds.images_to_numpy(include_filenames=True)
    assert len(imgs_plus_fnames) == len(imgs)
    assert os.path.isfile(imgs_plus_fnames[0][-1])
    shutil.rmtree(ds.tmp_location)


def test_008_ds_gt_to_numpy():
    ds = ds_008()
    labs = ds.gt_to_numpy()
    assert len(labs) > 0
    assert len(labs) == 24
    assert np.all([item.shape == (512, 512) for item in labs])
    shutil.rmtree(ds.tmp_location)
