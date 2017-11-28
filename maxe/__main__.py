import sys
from os import path

from .utils import fout, ferr
from .parser import proc_file


def main(args):
    for arg in args:
        if not path.isfile(arg):
            ferr("'{}' is not a file", arg)
            continue
        print(proc_file(arg))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
