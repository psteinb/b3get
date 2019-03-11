import os
import glob
import requests
import zipfile
import tifffile

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
        self.datasetid = baseurl.rstrip('/').split('/')[-1]

    def title(self):
        """ retrieve the title of the dataset """
        r = requests.get(self.baseurl)
        hdoc = BeautifulSoup(r.text, 'html.parser')
        return hdoc.title.string

    def list_images(self, absolute_url=False):
        """ retrieve the list of images for this dataset """
        values = []
        r = requests.get(self.baseurl)
        hdoc = BeautifulSoup(r.text, 'html.parser')
        all_links = hdoc.find_all('a')
        for anc in all_links:
            href = anc.get('href')
            if len(href) > 0 and "zip" in href and "images" in href:
                url = href if not absolute_url else "/".join([self.baseurl, href])
                values.append(url)
        return values

    def list_gt(self, absolute_url=False):
        """ retrieve the list of images for this dataset """
        values = []
        r = requests.get(self.baseurl)
        hdoc = BeautifulSoup(r.text, 'html.parser')
        all_links = hdoc.find_all('a')
        for anc in all_links:
            href = anc.get('href')
            if len(href) > 0 and "zip" in href and ("foreground" in href or "labels" in href):
                url = href if not absolute_url else "/".join([self.baseurl, href])
                values.append(url)
        return values

    def pull_files(self, filelist, rex=""):
        """ given a regular expression <rex>, download the files matching it from the dataset site """

        imgs = filter_files(filelist, rex)
        done = []
        if len(imgs) == 0:
            print("no images found matching {}".format(rex))
            return done

        tmp = tmp_location()
        dst = os.path.join(tmp,self.datasetid)
        if not os.path.exists(dst):
            os.makedirs(dst)

        for zurl in imgs:
            url = "/".join([self.baseurl, zurl])
            exp_size = size_of_content(url)
            fname = os.path.split(zurl)[-1]
            dstf = os.path.join(dst, fname)
            if os.path.exists(dstf) and os.path.isfile(dstf) and os.stat(dstf).st_size == exp_size:
                print('{0} already exists in {1} with the correct size {2} kB, skipping it'.format(fname, dst, exp_size/(1024.*1024.)))
                done.append(dstf)
                continue

            r = requests.get(url)
            assert r.ok, "unable to access URL: {}".format(url)
            print('downloading {0} ({1:.4} MB)'.format(zurl,exp_size/(1024.*1024.*1024.)))
            pulled_bytes = BytesIO(r.content)

            with open(dstf, 'wb') as fo:
                fo.write(pulled_bytes.read())

            if os.stat(dstf).st_size == exp_size:
                print("downloaded {0} to {1} ({2:.4} MB)".format(url, dstf, exp_size/(1024.*1024.*1024.)))
                done.append(dstf)
            else:
                print("download of {0} to {1} failed ({2} != {3} B)".format(url, dstf, exp_size, os.stat(dstf).st_size ))

        return done

    def pull_images(self, rex=""):
        """ given a regular expression <rex>, download the image files matching it from the dataset site """
        return self.pull_files(self.list_images(), rex)

    def pull_gt(self, rex=""):
        """ given a regular expression <rex>, download the ground truth files matching it from the dataset site """
        return self.pull_files(self.list_gt(), rex)


    def extract_files(self, filelist, dstdir):

        value = []
        if not (os.path.exists(dstdir) and os.path.isdir(dstdir)):
            print('{0} does not exists, will not extract anything to it')
            return value

        for fn in filelist:
            before = set(glob.glob(os.path.join(dstdir, "*")))
            with zipfile.ZipFile(fn, 'r') as zf:
                print('extracting ', fn)
                zf.extractall(dstdir)
                zf.close()
            after = set(glob.glob(os.path.join(dstdir, "*")))
            xpaths = after.difference(before)

            for entry in xpaths:
                value.extend(glob.glob(os.path.join(entry, "*tif")))

        return value


    def extract_images(self):
        """ check tmp_location for downloaded image zip files, if anything is found, extract them """

        tmp = tmp_location()
        globstmt = os.path.join(tmp, self.datasetid,"{did}*images*zip".format(did=self.datasetid))
        cands = glob.glob(globstmt)
        if not cands:
            print("E nothing found at",globstmt)
            return []

        datasetdir = os.path.join(tmp, self.datasetid)

        if not os.path.exists(datasetdir):
            os.makedirs(datasetdir)

        return self.extract_files(cands, datasetdir)

    def extract_gt(self):
        """ given a regular expression <rex>, download the ground truth files matching it from the dataset site """

        tmp = tmp_location()
        fg = os.path.join(tmp, self.datasetid,"{did}*foreground*zip".format(did=self.datasetid))
        cands = glob.glob(fg)
        labs = os.path.join(tmp, self.datasetid,"{did}*labels*zip".format(did=self.datasetid))
        cands.extend(glob.glob(labs))
        if not cands:
            return []

        datasetdir = os.path.join(tmp, self.datasetid)

        if not os.path.exists(datasetdir):
            os.makedirs(datasetdir)

        return self.extract_files(cands, datasetdir)

    def to_numpy(self, folder, glob_stmt="*tif"):
        """ given a folder, sort the found .tif files and try to open them with tifffile and return a list of numpy arrays """
        value = []
        if not os.path.exists(folder):
            return value

        glob_stmt = os.path.join(folder, glob_stmt)
        files = glob.glob(glob_stmt)
        if not files:
            print('nothing found at', glob_stmt)
            return value

        for fn in files:
            try:
                value.append(tifffile.imread(fn))
            except Exception as ex:
                print('unable to open {0} with tifffile due to {1}'.format(fn, ex))

        return value


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
