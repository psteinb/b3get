# b3get

A python module to download [Broad Bioimage Benchmark Collection](https://data.broadinstitute.org/bbbc/image_sets.html) images.

Intended Usage:

``` python
import b3get

train, test = b3get.pull(6, test_split = .2)
```

If you like the idea for this repo, please drop me a star. Due to time constraints, I will concentrate on dataset [06](https://data.broadinstitute.org/bbbc/BBBC006/), [24](https://data.broadinstitute.org/bbbc/BBBC024/) and [27](https://data.broadinstitute.org/bbbc/BBBC027/). If your dataset is not among those, please consider contributing.
