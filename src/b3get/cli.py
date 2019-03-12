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
import os
import sys
import traceback
from b3get import datasets
from b3get.utils import filter_files


class b3get_cli(object):

    def __init__(self, args=sys.argv):
        self.exit_code = 1
        self.args = args
        self.top_parser = argparse.ArgumentParser(
            description='Pretends to be git',
            usage='''b3get <command> [<args>]

The most commonly used git commands are:
   pull       download dataset
   list       list available datasets
''')
        self.top_parser.add_argument('command', help='Subcommand to run')

        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = self.top_parser.parse_args(args[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command',args[1:2])
            self.top_parser.print_help()

        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def pull(self):
        parser = argparse.ArgumentParser(
            description='download dataset')
        # prefixing the argument with -- means it's optional
        parser.add_argument('-o','--to', action='store', default='.', type=str,
                            help='directory where to store the downloaded dataset (error if it doesn\'t exist')
        parser.add_argument('--rex', action='store', type=str, default='',
                            help='regular expression to limit the images to download')
        parser.add_argument('-x', '--experimental', default=True, action='store_true',
                            help='try an unconfigured dataset')
        parser.add_argument('--lrex', action='store', type=str,
                            help='regular expression to limit the labels to download')
        parser.add_argument('-n','--dryrun', action='store_true', default=False,
                            help='don\'t download, just print filenames')
        parser.add_argument('datasets', nargs='+', help='dataset(s) to download')
        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command (git) and the subcommand (commit)
        args = parser.parse_args(self.args[2:])
        print(args)
        if not hasattr(args,'datasets'):
            print('no datasets given',args)
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

            files = ds.list_images()
            files = filter_files(files, args.rex)

            gt = ds.list_gt()
            files.extend(filter_files(gt, args.lrex))

            if args.dryrun:
                for fname in files:
                    print('pulling',fname)
            else:
                ds.pull_files(files, args.to)

        self.exit_code = 0

    def help(self):
        self.top_parser.print_help()

    def list(self):
        parser = argparse.ArgumentParser(
            description='list available datasets')
        # NOT prefixing the argument with -- means it's not optional
        #parser.add_argument('repository')
        args = parser.parse_args(self.args[2:])

        av = [6,8,24,27]

        print("\n".join([ "{0:03}".format(item) for item in av ]))
        self.exit_code = 0

    def list(self):
        parser = argparse.ArgumentParser(
            description='list available datasets')
        # NOT prefixing the argument with -- means it's not optional
        #parser.add_argument('repository')
        args = parser.parse_args(self.args[2:])
        av = [6,8,24,27]

        print("\n".join(["{0:03}".format(item) for item in av]))
        self.exit_code = 0

    def show(self):
        parser = argparse.ArgumentParser(
            description='show URLs for given dataset')
        parser.add_argument('datasets', nargs='+', help='dataset(s) to download')
        parser.add_argument('-x', '--experimental', default=True, action='store_true', help='try an unconfigured dataset')
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
            files.extend(ds.list_gt())

            for fname in files:
                print(os.path.join(ds.baseurl, fname))
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
