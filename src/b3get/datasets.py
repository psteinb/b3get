from __future__ import absolute_import, print_function, with_statement

import os
import glob
import requests
import zipfile
import tifffile
import six

from bs4 import BeautifulSoup
from b3get.utils import tmp_location, filter_files, size_of_content, wrap_serial_download_file
from tqdm import trange, tqdm
from multiprocessing import Pool, freeze_support, RLock, cpu_count


class dataset():
    """ base class that offers methods which all deriving classes can override if needed """

    def __init__(self, baseurl=None, datasetid=None):
        """
        constructor of dataset given a baseurl or dataasetid (baseurl has precedence)
        - will throw RuntimeError if neither <baseurl> nor <datasetid> is given
        - will throw RuntimeError if <datasetid> invalid (greater than 42)
        - will throw RuntimeError if URL <baseurl> is not reachable
        """
        if not baseurl:
            if not datasetid:
                raise RuntimeError('No URL or datasetid given to b3get. Nothing todo then.')
            elif datasetid < 43:
                baseurl = "https://data.broadinstitute.org/bbbc/BBBC{0:03}/".format(datasetid)
            else:
                raise RuntimeError('Dataset id {} given to b3get invalid.'.format(datasetid))

        r = requests.get(baseurl)
        if not r.ok:
            raise RuntimeError('No dataset can be reached at {}'.format(baseurl))

        self.baseurl = baseurl
        self.datasetid = baseurl.rstrip('/').split('/')[-1]
        self.tmp_location = os.path.join(tmp_location(), self.datasetid)

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

    def pull_files(self, filelist, dstdir=None, rex="", nprocs=1):
        """ given a regular expression <rex>, download the files matching it from the dataset site
        filelist: a list of file names (no paths)
        dstdir  : destination folder where to download files to
        rex     : filter <filelist> for this regex string
        nprocs  : perform download with this many processors (nprocs=-1 means all CPUs)
        """

        imgs = filter_files(filelist, rex) if rex else filelist
        done = []
        if len(imgs) == 0:
            print("no images found matching {}".format(rex))
            return done

        if not dstdir:
            dstdir = self.tmp_location
        if not os.path.exists(dstdir):
            print("creating {}".format(dstdir))
            os.makedirs(dstdir)

        fullurls = []

        for zurl in imgs:
            url = "/".join([self.baseurl, zurl]) if not self.baseurl in zurl else zurl
            exp_size = size_of_content(url)
            fname = os.path.split(zurl)[-1]
            dstf = os.path.join(dstdir, fname)
            if os.path.exists(dstf) and os.path.isfile(dstf) and os.stat(dstf).st_size == exp_size:
                print('{0} already exists in {1} with the correct size {2:04.4} kB, skipping it'.format(fname, dstdir, exp_size/(1024.*1024.)))
                done.append(dstf)
                continue
            fullurls.append(url)

        nprocs = cpu_count() if nprocs < 0 else nprocs
        freeze_support()  # for Windows support
        p = Pool(nprocs,
                 # again, for Windows support
                 initializer=tqdm.set_lock, initargs=(RLock(),))

        dstfolders = [dstdir]*len(fullurls)
        cbytes = [1024*1024]*len(fullurls)
        procids = [item % nprocs for item in range(len(fullurls))]

        zipped_args = zip(fullurls, dstfolders, cbytes, procids)
        dpaths = p.map(wrap_serial_download_file, zipped_args)

        for i in range(len(fullurls)):
            fpath = dpaths[i]
            url = fullurls[i]
            exp_size = size_of_content(url)
            if os.path.isfile(fpath) and os.stat(fpath).st_size == exp_size:
                print("downloaded {0} to {1} ({2:.4} MB)".format(url, fpath, exp_size/(1024.*1024.*1024.)))
                done.append(fpath)
            else:
                print("download of {0} to {1} failed ({2} != {3} B)".format(url, fpath, exp_size, os.stat(fpath).st_size))

        return done

    def pull_images(self, rex=""):
        """ given a regular expression <rex>, download the image files matching it from the dataset site """
        return self.pull_files(self.list_images(), rex=rex)

    def pull_gt(self, rex=""):
        """ given a regular expression <rex>, download the ground truth files matching it from the dataset site """
        return self.pull_files(self.list_gt(), rex=rex)

    def extract_files(self, filelist, dstdir):
        """ unpack each file in <filelist> to folder <dstdir> """

        value = []
        if not (os.path.exists(dstdir) and os.path.isdir(dstdir)):
            print('{0} does not exists, will not extract anything to it')
            return value

        for fn in filelist:
            xpaths = None
            with zipfile.ZipFile(fn, 'r') as zf:
                print('extracting ', fn)
                zf.extractall(dstdir)
                xpaths = zf.namelist()
                zf.close()

            for entry in xpaths:
                loc = os.path.join(dstdir,entry)
                basedir, fname = os.path.split(loc)
                if os.path.isfile(loc) and ".tif" in fname and "__MACOSX" not in basedir:
                    value.append(loc)

        return value

    def extract_images(self, folder=None):
        """ check folder for downloaded image zip files, if anything is found, extract them """

        if not folder:
            folder = self.tmp_location
        globstmt = os.path.join(folder, "{did}*images*zip".format(did=self.datasetid))
        cands = glob.glob(globstmt)
        if not cands:
            print("E nothing found at", globstmt)
            return []

        datasetdir = os.path.join(folder, self.datasetid)

        if not os.path.exists(datasetdir):
            os.makedirs(datasetdir)

        return self.extract_files(cands, datasetdir)

    def extract_gt(self, folder=None):
        """ extract the ground truth files found in <folder>, returns list of files extracted """

        if not folder:
            folder = self.tmp_location
        fg = os.path.join(folder, "{did}*foreground*zip".format(did=self.datasetid))
        cands = glob.glob(fg)
        if not cands:
            print('E nothing found for', fg)

        labs = os.path.join(folder, "{did}*labels*zip".format(did=self.datasetid))
        cands.extend(glob.glob(labs))
        if not cands:
            print('E nothing found for', labs)
            return []

        datasetdir = os.path.join(folder, self.datasetid)

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

    def __init__(self, baseurl=None, datasetid=6):
        if six.PY3:
            super().__init__(baseurl=baseurl, datasetid=datasetid)
        else:
            dataset.__init__(self, baseurl=baseurl, datasetid=datasetid)


class ds_008(dataset):

    def __init__(self, baseurl=None, datasetid=8):
        if six.PY3:
            super().__init__(baseurl=baseurl, datasetid=datasetid)
        else:
            dataset.__init__(self, baseurl=baseurl, datasetid=datasetid)


class ds_027(dataset):

    def __init__(self, baseurl=None, datasetid=27):
        if six.PY3:
            super().__init__(baseurl=baseurl, datasetid=datasetid)
        else:
            dataset.__init__(self, baseurl=baseurl, datasetid=datasetid)


class ds_024(dataset):

    def __init__(self, baseurl=None, datasetid=24):
        if six.PY3:
            super().__init__(baseurl=baseurl, datasetid=datasetid)
        else:
            dataset.__init__(self, baseurl=baseurl, datasetid=datasetid)
