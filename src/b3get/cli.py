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
import argparse
import sys


class b3get_cli(object):

    def __init__(self, args = sys.argv):
        parser = argparse.ArgumentParser(
            description='Pretends to be git',
            usage='''b3get <command> [<args>]

The most commonly used git commands are:
   pull       download dataset
   list       list available datasets
''')
        parser.add_argument('command', help='Subcommand to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(args[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command',args[1:2])
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def pull(self):
        parser = argparse.ArgumentParser(
            description='download dataset')
        # prefixing the argument with -- means it's optional
        parser.add_argument('--to', action='store', type=str, help='directory where to store the downloaded dataaset')
        parser.add_argument('--rex', action='store', type=str, help='regular expression to limit the images to download')
        parser.add_argument('--lrex', action='store', type=str, help='regular expression to limit the labels to download')
        parser.add_argument('dataset', help='dataset to download')
        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command (git) and the subcommand (commit)
        args = parser.parse_args(sys.argv[2:])
        if not hasattr(args,'dataset'):
            print('no dataset given')
            parser.print_help()
            exit(1)
        print('Downloading , amend=%s' % args.amend)

    def list(self):
        parser = argparse.ArgumentParser(
            description='list available datasets')
        # NOT prefixing the argument with -- means it's not optional
        #parser.add_argument('repository')
        args = parser.parse_args(sys.argv[2:])
        av = [6,8,24,27]

        print("\n".join([ "{0:03}".format(item) for item in av ]))


def main(args=sys.argv):
    b3get_cli(args)
    # args = parser.parse_args(args=args)
    # print(args.names)
