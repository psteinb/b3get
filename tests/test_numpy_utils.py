import numpy as np
import os
import pytest
import tempfile

from b3get.utils import chunk_npz

@pytest.fixture
def list_of_ndarrays():
    nplist = [np.ones(shape=(256, 256), dtype='uint32') for n in range(16)]  # 16*256KB
    for idx in range(len(nplist)):
        nplist[idx].fill(int(idx))
    return nplist


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
    fnames = sorted(npt.files, key=lambda x: int(x.split('_')[-1]))
    assert 'arr_0' in fnames
    assert 'arr_15' in fnames
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

    frontf = sorted(front.files, key=lambda x: int(x.split('_')[-1]))
    backf = sorted(back.files, key=lambda x: int(x.split('_')[-1]))

    assert len(frontf) > 0
    assert len(backf) > 0


    assert front[frontf[0]].nbytes > 0
    assert back[backf[0]].nbytes > 0

    assert front[frontf[0]].shape == (256,256)
    assert back[backf[0]].shape == (256,256)

    assert front[frontf[0]].shape == list_of_ndarrays[0].shape
    assert np.all(front[frontf[0]] == list_of_ndarrays[0])

    assert back[backf[-1]].shape == list_of_ndarrays[-1].shape
    assert np.all(back[backf[-1]] == list_of_ndarrays[-1])
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


def test_with_quarter_gb():

    list_of_ndarrays = [np.ones(shape=(256, 256, 256), dtype='uint32') for i in range(16)]
    for idx in range(len(list_of_ndarrays)):
        list_of_ndarrays[idx].fill(int(idx))

    assert list_of_ndarrays[0][0,0,0] == 0
    assert list_of_ndarrays[1][0,0,0] == 1
    assert list_of_ndarrays[2][0,0,0] == 2

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

    frontf = sorted(front.files, key=lambda x: int(x.split('_')[-1]))
    backf = sorted(back.files, key=lambda x: int(x.split('_')[-1]))

    assert len(frontf) > 0
    assert len(backf) > 0
    assert len(back) == len(frontf)

    assert front[frontf[0]].nbytes > 0
    assert back[backf[0]].nbytes > 0

    assert front[frontf[0]].shape == (256, 256, 256)
    assert back[backf[0]].shape == (256, 256, 256)

    assert front[frontf[0]].shape == list_of_ndarrays[0].shape
    assert np.all(front[frontf[0]] == list_of_ndarrays[0])

    assert back[backf[-1]].shape == list_of_ndarrays[-1].shape
    assert np.all(back[backf[-1]] == list_of_ndarrays[-1])
    [os.remove(f) for f in files]
