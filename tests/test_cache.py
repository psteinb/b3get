import tempfile
import os
from b3get.utils import tmp_location


def test_has_tempdir():
    assert tempfile.gettempdir()


def test_create_tempdir():
    assert tempfile.gettempdir()
    tdir = tempfile.mkdtemp()
    assert os.path.exists(tdir)
    print("\n", tdir)
    os.removedirs(tdir)


def test_b3get_tempdir():
    tdir = tmp_location()
    assert os.path.exists(tdir)
    assert os.path.isdir(tdir)

    os.removedirs(tdir)


def test_b3get_tempdir_reuse():
    tmp = tempfile.gettempdir()
    exp = os.path.join(tmp, 'random-b3get')
    os.makedirs(exp)
    tdir = tmp_location()
    assert tdir == exp
    os.removedirs(tdir)


def test_b3get_tempdir_double_call():
    exp = tmp_location()
    tdir = tmp_location()
    assert tdir == exp
    os.removedirs(tdir)
