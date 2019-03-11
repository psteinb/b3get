import os
import requests
from bs4 import BeautifulSoup
from b3get.utils import *
from io import BytesIO


class dataset():
    """ base class that offers methods which all deriving classes can override if needed """

    def __init__(self, baseurl=None):
        """
        constructor of dataset given a baseurl
        - will throw RuntimeError if no URL is given
        - will throw RuntimeError if URL <baseurl> is not reachable
        """
        if not baseurl:
            raise RuntimeError('No URL given to b3get. Nothing todo then.')
        r = requests.get(baseurl)
        if not r.ok:
            raise RuntimeError('No dataset can be reached at {}'.format(baseurl))

        self.baseurl = baseurl
        self.datasetid = baseurl.split('/')[-1]

    def title(self):
        """ retrieve the title of the dataset """
        r = requests.get(self.baseurl)
        hdoc = BeautifulSoup(r.text, 'html.parser')
        return hdoc.title.string

    def list_images(self):
        """ retrieve the list of images for this dataset """
        values = []
        r = requests.get(self.baseurl)
        hdoc = BeautifulSoup(r.text, 'html.parser')
        all_links = hdoc.find_all('a')
        for anc in all_links:
            href = anc.get('href')
            if len(href) > 0 and "zip" in href and "images" in href:
                values.append(href)
        return values

    def pull_images(self, rex=""):
        """ given a regular expression <rex>, download the files matching it from the dataset site """
        imgs = filter_files(self.list_images(), rex)
        done = []
        if len(imgs) == 0:
            print("no images found matching {}".format(rex))
            return done

        tmp = tmp_location()
        dst = os.path.join(tmp,self.datasetid)
        if not os.path.exists(dst):
            os.makedirs(dst)

        for zurl in imgs:
            url = "/".join([self.baseurl,zurl])
            r = requests.get(url)
            assert r.ok, "unable to access URL: {}".format(url)
            pulled_bytes = BytesIO(r.content)
            dstf = os.path.join(dst, os.path.split(zurl)[-1])
            with open(dstf, 'wb') as fo:
                fo.write(pulled_bytes.read())
            print("downloaded {0} to {1}".format(url, dstf))
            done.append(dstf)

        return done


class ds_006(dataset):

    __baseurl = "https://data.broadinstitute.org/bbbc/BBBC006/"

    def __init__(self, baseurl=None):
        super().__init__(baseurl=ds_006.__baseurl if not baseurl else baseurl)


class ds_008(dataset):

    __baseurl = "https://data.broadinstitute.org/bbbc/BBBC008/"

    def __init__(self, baseurl=None):
        super().__init__(baseurl=ds_008.__baseurl if not baseurl else baseurl)



class ds_027(dataset):

    __baseurl = "https://data.broadinstitute.org/bbbc/BBBC027/"

    def __init__(self, baseurl=None):
        super().__init__(baseurl=ds_027.__baseurl if not baseurl else baseurl)
