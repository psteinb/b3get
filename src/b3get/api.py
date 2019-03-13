import os
from b3get.datasets import *


def to_numpy(dataset_id=None, labels_match='foreground'):
    """ function to download and convert dataset of ID <dataeset_id>
    return value: tuple (size 2)
    - item 0: images associated with this dataset
    - item 1: labels selected according to <labels_match>
    """

    value = (None, None)
    dsint = int(dataset_id)
    ds = None
    try:
        if dsint not in [6, 8, 24, 27]:
            print('support for BBBC{0:03} planned, but not thoroughly tested yet'.format(dsint))
            ds = eval('dataset(datasetid="BBBC{0:03}")'.format(dsint))
        else:
            ds = eval('ds_{0:03}()'.format(dsint))
    except Exception as ex:
        print('unable to create dataset from', dataset_id, ex)
        return value

    imgs = ds.pull_images()
    ximgs = ds.extract_images()

    if len(ximgs) > 0 and imgs:
        ximgs = sorted(ximgs)
        basepath = os.path.split(ximgs[0])[0]
        value = (ds.folder_to_numpy(basepath), None)
    else:
        print('extraction of images failed\n', ximgs)

    labs = ds.pull_gt(labels_match)
    xlabs = ds.extract_gt()
    if len(xlabs) > 0 and labs:
        xlabs = sorted(xlabs)
        basepath = os.path.split(xlabs[0])[0]
        value = (value[0], ds.folder_to_numpy(basepath))
    else:
        print('extraction of labels failed\n', xlabs, labels_match)

    return value
