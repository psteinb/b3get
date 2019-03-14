import numpy as np
import os
import pytest
import tempfile

from b3get.utils import chunk_npz

@pytest.fixture
def list_of_ndarrays():
    return [np.ones(shape=(256,256), dtype='uint32')*n for n in range(16)]  # 16*256KB


def test_fixture_values(list_of_ndarrays):
    front = list_of_ndarrays[0]
    back = list_of_ndarrays[-1]
    assert np.all(front[:16, 0] == 0)
    assert np.all(back[:16, 0] == 15)


def test_np_savez(list_of_ndarrays):
    tmpf = tempfile.mktemp()
    tmpf += '.npz'

    np.savez(tmpf, *list_of_ndarrays)
    assert os.path.isfile(tmpf), tmpf
    assert os.stat(tmpf).st_size >= 16*256*1024
    os.remove(tmpf)


def test_np_savez_reopen(list_of_ndarrays):
    tmpf = tempfile.mktemp()
    tmpf += '.npz'

    np.savez(tmpf, *list_of_ndarrays)
    assert os.path.isfile(tmpf), tmpf
    assert os.stat(tmpf).st_size >= 16*256*1024

    npt = np.load(tmpf)
    assert len(npt.files) == 16
    assert npt.files[0] == 'arr_0'
    assert npt.files[-1] == 'arr_15'
    front = npt['arr_0']
    back = npt['arr_15']
    assert np.all(front[:16, 0] == 0)
    assert np.all(back[:16, 0] == 15)
    os.remove(tmpf)


def test_in_chunks(list_of_ndarrays):
    tmpf = tempfile.mktemp()
    files = chunk_npz(list_of_ndarrays, tmpf, .5)
    assert len(files) > 0
    assert len(files) == 8
    front_size = os.stat(files[0]).st_size
    back_size = os.stat(files[-1]).st_size

    assert front_size <= 512*1024
    assert front_size > 22

    assert back_size <= 512*1024
    assert back_size > 22

    front = np.load(files[0])
    back = np.load(files[-1])

    assert len(front.files) > 0
    assert len(back.files) > 0

    assert front[front.files[0]].nbytes > 0
    assert back[back.files[0]].nbytes > 0

    assert front[front.files[0]].shape == (256,256)
    assert back[back.files[0]].shape == (256,256)

    assert front[front.files[0]].shape == list_of_ndarrays[0].shape
    assert np.all(front[front.files[0]] == list_of_ndarrays[0])

    assert back[back.files[-1]].shape == list_of_ndarrays[-1].shape
    assert np.all(back[back.files[-1]] == list_of_ndarrays[-1])
    [os.remove(f) for f in files]


def test_in_chunks_too_large(list_of_ndarrays):
    tmpf = tempfile.mktemp()
    files = chunk_npz(list_of_ndarrays, tmpf, 20)
    assert len(files) > 0
    assert len(files) == 1
    front_size = os.stat(files[0]).st_size

    assert front_size <= 512*1024
    assert front_size > 22

    [os.remove(f) for f in files]


def test_with_quarter_gb(list_of_ndarrays):

    for idx in range(len(list_of_ndarrays)):

        list_of_ndarrays[idx].resize(256, 256, 256)
        list_of_ndarrays[idx][:] = idx

    tmpf = tempfile.mktemp()
    files = chunk_npz(list_of_ndarrays, tmpf, 128)
    assert len(files) > 0
    assert len(files) == 8
    front_size = os.stat(files[0]).st_size
    back_size = os.stat(files[-1]).st_size

    assert front_size > 22
    assert back_size > 22

    front = np.load(files[0])
    back = np.load(files[-1])

    assert len(front.files) > 0
    assert len(back.files) > 0
    assert len(back.files) == len(front.files)

    assert front[front.files[0]].nbytes > 0
    assert back[back.files[0]].nbytes > 0

    assert front[front.files[0]].shape == (256, 256, 256)
    assert back[back.files[0]].shape == (256, 256, 256)

    assert front[front.files[0]].shape == list_of_ndarrays[0].shape
    assert np.all(front[front.files[0]] == list_of_ndarrays[0])

    assert back[back.files[-1]].shape == list_of_ndarrays[-1].shape
    assert np.all(back[back.files[-1]] == list_of_ndarrays[-1])
    [os.remove(f) for f in files]
