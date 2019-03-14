import numpy as np
import os
import pytest
import tempfile
import zipfile
import shutil
from b3get.utils import unzip_to


@pytest.fixture
def azipfile():
    basedir = tempfile.mkdtemp()

    input_files = [tempfile.mktemp(dir=basedir) for _ in range(16)]
    for idx, fn in enumerate(input_files):
        with open(fn, 'w') as of:
            of.write(str(idx))
            of.write('\t')
            of.write(fn)

    zip_path = tempfile.mktemp('.zip')
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for f in input_files:
            an = os.path.join(os.path.split(basedir)[-1], os.path.basename(f))
            zf.write(f, arcname=an)
        zf.close()
    return zip_path, input_files


def test_fixture_values(azipfile):
    zf, content = azipfile
    assert os.path.isfile(zf)
    assert os.stat(zf).st_size > 0

    with zipfile.ZipFile(zf, 'r') as zfo:
        nl = zfo.namelist()
        assert len(nl) == 16
        assert not nl[0].startswith('/tmp')

    os.remove(zf)
    [ os.remove(c) for c in content ]


def test_unzip_to_simple(azipfile):
    zf, src_files = azipfile
    somedir = tempfile.mkdtemp()
    files = unzip_to(zf, somedir)

    files = sorted(files)
    src_files = sorted(src_files)

    assert len(files) > 0
    assert len(files) == len(src_files)

    assert os.path.basename(files[0]) == os.path.basename(src_files[0])
    assert os.path.basename(files[-1]) == os.path.basename(src_files[-1])

    os.remove(zf)
    [ os.remove(c) for c in src_files ]
    shutil.rmtree(somedir)

def test_unzip_twice(azipfile):
    zf, src_files = azipfile
    somedir = tempfile.mkdtemp()
    files = unzip_to(zf, somedir)

    files = sorted(files)
    src_files = sorted(src_files)

    assert len(files) > 0
    assert len(files) == len(src_files)

    assert os.path.basename(files[0]) == os.path.basename(src_files[0])
    assert os.path.basename(files[-1]) == os.path.basename(src_files[-1])

    again = sorted(unzip_to(zf,somedir))

    assert len(again) > 0
    assert len(again) == len(src_files)

    assert os.path.basename(again[0]) == os.path.basename(src_files[0])
    assert os.path.basename(again[-1]) == os.path.basename(src_files[-1])

    os.remove(zf)
    [ os.remove(c) for c in src_files ]
    shutil.rmtree(somedir)


def test_unzip_twice_impartial(azipfile):
    zf, src_files = azipfile
    somedir = tempfile.mkdtemp()
    files = unzip_to(zf, somedir)

    files = sorted(files)
    src_files = sorted(src_files)

    assert len(files) > 0
    assert len(files) == len(src_files)

    assert os.path.basename(files[0]) == os.path.basename(src_files[0])
    assert os.path.basename(files[-1]) == os.path.basename(src_files[-1])

    os.remove(files[-1])
    os.remove(files[-2])

    again = sorted(unzip_to(zf,somedir))

    assert len(again) > 0
    assert len(again) == len(src_files)

    assert os.path.basename(again[0]) == os.path.basename(src_files[0])
    assert os.path.basename(again[-1]) == os.path.basename(src_files[-1])

    os.remove(zf)
    [ os.remove(c) for c in src_files ]
    shutil.rmtree(somedir)
