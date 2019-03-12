from __future__ import print_function

import tempfile
import os
import shutil
from b3get.utils import tmp_location


def test_has_tempdir():
    assert tempfile.gettempdir()


def test_create_tempdir():
    assert tempfile.gettempdir()
    tdir = tempfile.mkdtemp()
    assert os.path.exists(tdir)
    print("\n", tdir)

    shutil.rmtree(tdir)


def test_b3get_tempdir():
    tdir = tmp_location()
    assert os.path.exists(tdir)
    assert os.path.isdir(tdir)

    shutil.rmtree(tdir)


def test_b3get_tempdir_reuse():
    tmp = tempfile.gettempdir()
    exp = os.path.join(tmp, 'random-b3get')
    os.makedirs(exp)
    tdir = tmp_location()
    assert tdir == exp
    shutil.rmtree(tdir)


def test_b3get_tempdir_double_call():
    exp = tmp_location()
    tdir = tmp_location()
    assert tdir == exp
    shutil.rmtree(tdir)
