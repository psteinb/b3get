"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mb3get` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``b3get.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``b3get.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
from __future__ import print_function, with_statement
import argparse
import inspect
import os
import sys
import traceback
from multiprocessing import cpu_count

from b3get import datasets
from b3get.utils import filter_files, size_of_content, chunk_npz
import b3get


class b3get_cli(object):

    def __init__(self, args=sys.argv):
        self.exit_code = 1
        self.args = args
        usage_str = '''b3get <command> [<args>]

The most commonly used commands are:\n'''

        for k in dir(self):
            if k.startswith('__'):
                continue
            if not callable(getattr(self, k)):
                continue

            dstr = inspect.getdoc(getattr(self, k))
            if dstr and len(dstr) > 0:
                usage_str += "\t{0}\t{1}\n".format(k, dstr)

        self.top_parser = argparse.ArgumentParser(
            description='',
            usage=usage_str)
        self.top_parser.add_argument('command', help='Subcommand to run')

        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = self.top_parser.parse_args(args[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command', args[1:2])
            self.top_parser.print_help()

        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def pull(self):
        """ download dataset """
        parser = argparse.ArgumentParser(
            description='download dataset')
        # prefixing the argument with -- means it's optional
        parser.add_argument('-o', '--to', action='store', default='.', type=str,
                            help='directory where to store the downloaded dataset (error if it doesn\'t exist')
        parser.add_argument('--rex', action='store', type=str, default='',
                            help='regular expression to limit the images to download')
        parser.add_argument('-x', '--experimental', default=True, action='store_true',
                            help='try an unconfigured dataset')
        parser.add_argument('--lrex', action='store', type=str,
                            help='regular expression to limit the labels to download')
        parser.add_argument('-n', '--dryrun', action='store_true', default=False,
                            help='don\'t download, just print filenames')
        parser.add_argument('-j', '--nprocs', action='store', default=1, type=int,
                            help='perform <nprocs> many parallel downloads')
        parser.add_argument('datasets', nargs='+', help='dataset(s) to download')
        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command (git) and the subcommand (commit)
        args = parser.parse_args(self.args[2:])
        nprocs = cpu_count() if args.nprocs < 0 else args.nprocs

        if not hasattr(args, 'datasets'):
            print('no datasets given', args)
            parser.print_help()
            return

        if not os.path.isdir(args.to):
            print('{0} does not exist, please create it first'.format(args.to))
            return

        for item in args.datasets:
            ds = None
            dsid = int(item)
            if not args.experimental:
                ds = eval('datasets.ds_{0:03}()'.format(dsid))
            else:
                ds = eval('datasets.dataset(baseurl="https://data.broadinstitute.org/bbbc/BBBC{0:03}/")'.format(dsid))

            print('fetching image information for dataset', dsid)
            files = ds.list_images()
            files = filter_files(files, args.rex)

            gt = ds.list_gt()
            files.extend(filter_files(gt, args.lrex))

            if args.dryrun:
                for fname in files:
                    print('[dryrun] pulling', os.path.join(ds.baseurl, fname))
            else:
                ds.pull_files(files, dstdir=args.to, nprocs=nprocs)

        self.exit_code = 0

    def resave(self):
        """ resave a dataset to .npz format """
        parser = argparse.ArgumentParser(
            description='resave dataset to .npz format')
        # prefixing the argument with -- means it's optional
        parser.add_argument('-o', '--to', action='store', default='.', type=str,
                            help='directory where to store the downloaded dataset (error if it doesn\'t exist')
        parser.add_argument('--rex', action='store', type=str, default='',
                            help='regular expression to limit the images to download')
        parser.add_argument('-x', '--experimental', default=True, action='store_true',
                            help='try an unconfigured dataset')
        parser.add_argument('--lrex', action='store', type=str,
                            help='regular expression to limit the labels to download')
        parser.add_argument('-n', '--dryrun', action='store_true', default=False,
                            help='don\'t download, just print filenames')

        parser.add_argument('-m', '--max_megabytes', action='store', default=0, type=int,
                            help='produce at max files that are close to max_megabytes in size (0 refers to one single blob)')

        parser.add_argument('-j', '--nprocs', action='store', default=1, type=int,
                            help='perform <nprocs> many parallel downloads')
        parser.add_argument('datasets', nargs='+', help='dataset(s) to download')
        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command (git) and the subcommand (commit)
        args = parser.parse_args(self.args[2:])
        nprocs = int(cpu_count() if args.nprocs < 0 else args.nprocs)

        if not hasattr(args, 'datasets'):
            print('no datasets given', args)
            parser.print_help()
            return

        if not os.path.isdir(args.to):
            print('{0} does not exist, please create it first'.format(args.to))
            return

        for item in args.datasets:
            ds = None
            dsid = int(item)
            if not args.experimental:
                ds = eval('datasets.ds_{0:03}()'.format(dsid))
            else:
                ds = eval('datasets.dataset(baseurl="https://data.broadinstitute.org/bbbc/BBBC{0:03}/")'.format(dsid))

            print('fetching image information for dataset', dsid)
            files = ds.list_images()
            imgs = filter_files(files, args.rex)
            files = imgs[:]

            gt = ds.list_gt()
            gt = filter_files(gt, args.lrex)
            files.extend(gt)

            if args.dryrun:
                for fname in files:
                    print('[dryrun] pulling', os.path.join(ds.baseurl, fname))
                return

            zipimgs = ds.pull_files(imgs, dstdir=args.to, nprocs=nprocs)
            zipgt = ds.pull_files(gt, dstdir=args.to, nprocs=nprocs)

            if zipimgs:
                npimgs = ds.zips_to_numpy(zipimgs, nprocs=nprocs)

                fname = os.path.join(args.to, 'BBBC{0:03}_images'.format(dsid))
                npzimgs = chunk_npz(npimgs, fname, args.max_megabytes)
                if npzimgs:
                    print('wrote ', ", ".join(npzimgs))
                    self.exit_code = 0

            if zipgt:
                npgt = ds.zips_to_numpy(zipgt, nprocs=nprocs)

                fname = os.path.join(args.to, 'BBBC{0:03}_labels'.format(dsid))
                npzgt = chunk_npz(npgt, fname, args.max_megabytes)
                if npzgt:
                    print('wrote ', ", ".join(npzgt))
                    self.exit_code = 0

        self.exit_code = 0

    def help(self):
        """show help message"""
        self.top_parser.print_help()

    def list(self):
        """list available datasets"""
        parser = argparse.ArgumentParser(
            description='list tested available datasets (anything else is experimental)')
        # NOT prefixing the argument with -- means it's not optional
        # parser.add_argument('repository')
        args = parser.parse_args(self.args[2:])
        if 'help' in args:
            parser.print_help()
            return

        av = [6, 8, 24, 27]
        for i in av:
            dsid = "BBBC{0:03}".format(i)
            if dsid in datasets.TESTED_DATASETS.keys():
                print("BBBC{0:03} {1}".format(i, datasets.TESTED_DATASETS[dsid]))

        self.exit_code = 0

    def show(self):
        """show files contained in a dataset"""
        parser = argparse.ArgumentParser(
            description='show URLs for given dataset')
        parser.add_argument('datasets', nargs='+', help='dataset(s) to download')
        parser.add_argument('--rex', action='store', type=str, default=None,
                            help='regular expression to limit the images to download')
        parser.add_argument('-x', '--experimental', default=True, action='store_true',
                            help='try an unconfigured dataset')
        parser.add_argument('--lrex', action='store', type=str, default=None,
                            help='regular expression to limit the labels to download')
        parser.add_argument('-s', '--add_size', default=False, action='store_true', help='add size in MB of file')
        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command (git) and the subcommand (commit)
        args = parser.parse_args(self.args[2:])
        if not hasattr(args, 'datasets'):
            print('no datasets given', args)
            parser.print_help()
            return

        for item in args.datasets:
            ds = None
            dsid = int(item)
            if not args.experimental:
                ds = eval('datasets.ds_{0:03}()'.format(dsid))
            else:
                ds = eval('datasets.dataset(baseurl="https://data.broadinstitute.org/bbbc/BBBC{0:03}/")'.format(dsid))

            files = ds.list_images()
            files = filter_files(files, rex=args.rex)
            gt = ds.list_gt()
            gt = filter_files(gt, rex=args.lrex)
            files.extend(gt)

            for fname in files:
                url = os.path.join(ds.baseurl, fname)
                if args.add_size:
                    size = size_of_content(url)
                    print("{0:10.04}MB\t{1}".format(size/(1024.*1024.*1024), url))
                else:
                    print(url)

        self.exit_code = 0

    def version(self):
        """ show the version of b3get """

        print('b3get', b3get.__version__)
        self.exit_code = 0


def main(args=sys.argv):
    try:
        app = b3get_cli(args)
    except Exception as ex:
        print('b3get_cli failed with', ex)
        traceback.print_exc(file=sys.stdout)
        return 1
    else:
        return app.exit_code
    # args = parser.parse_args(args=args)
    # print(args.names)
