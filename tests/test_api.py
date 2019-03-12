import os
import shutil
from b3get.utils import tmp_location

from b3get import to_numpy
import numpy as np


def test_available():
    assert dir(to_numpy)


def test_wrong_ds():
    assert to_numpy(9) == (None, None)


def test_008():
    tgt = os.path.join(tmp_location(), 'BBBC008')

    if os.path.exists(tgt):
        shutil.rmtree(tgt)

    imgs, labs = to_numpy(8)
    assert len(imgs) > 0
    assert len(imgs) == 24

    assert isinstance(imgs[0], np.ndarray)
    assert imgs[0].shape == (512, 512)
    assert imgs[0].dtype == np.uint8

    assert isinstance(labs[0], np.ndarray)
    assert labs[0].shape == (512, 512)
    assert imgs[0].dtype == np.uint8

    shutil.rmtree(tgt)
