# b3get

A python module to download [Broad Bioimage Benchmark Collection](https://data.broadinstitute.org/bbbc/image_sets.html) images.

Usage:

``` python
import b3get

images, labels = b3get.to_numpy(6)
```
The call illustrated above creates 2 python lists. Each list contains a set of `numpy.ndarray` objects which yield the images of the dataset (`images`) or the labels (`labels`). 

If you like the idea for this repo, please drop me a star. Due to time constraints, I will concentrate on dataset [06](https://data.broadinstitute.org/bbbc/BBBC006/), [24](https://data.broadinstitute.org/bbbc/BBBC024/) and [27](https://data.broadinstitute.org/bbbc/BBBC027/). If your dataset is not among those, please consider contributing.
