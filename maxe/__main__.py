import sys
from os import path
from pprint import pprint

from .utils import fout, ferr
from .lisp import parse_file


def main(args):
    for arg in args:
        with open(arg) as f:
            for i in parse_file(f):
                print(i)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
