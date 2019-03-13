# b3get [![Build Status](https://travis-ci.com/psteinb/b3get.svg?branch=master)](https://travis-ci.com/psteinb/b3get) [![codecov](https://codecov.io/gh/psteinb/b3get/branch/master/graph/badge.svg)](https://codecov.io/gh/psteinb/b3get)

A python module to download [Broad Bioimage Benchmark Collection](https://data.broadinstitute.org/bbbc/image_sets.html) images.

## Usage

### As a python module

``` python
import b3get

images, labels = b3get.to_numpy(6)
```
The call illustrated above creates 2 python lists. Each list contains a set of `numpy.ndarray` objects which yield the images of the dataset (`images`) or the labels (`labels`). 

If you like the idea for this repo, please drop me a star. Due to time constraints, I will concentrate on dataset [06](https://data.broadinstitute.org/bbbc/BBBC006/), [24](https://data.broadinstitute.org/bbbc/BBBC024/) and [27](https://data.broadinstitute.org/bbbc/BBBC027/). If your dataset is not among those, please consider contributing.

### From the Command-line

- to list available datasets

``` shell
$ b3get list
BBBC006 Human U2OS cells (out of focus) 
BBBC008 Human HT29 colon-cancer cells   
BBBC024 3D HL60 Cell Line (synthetic data)
BBBC027 3D Colon Tissue (synthetic data)
```

- to show the URLS for a given dataset

``` shell
$ b3get show 08
https://data.broadinstitute.org/bbbc/BBBC008/BBBC008_v1_images.zip
https://data.broadinstitute.org/bbbc/BBBC008/BBBC008_v1_foreground.zip
```

