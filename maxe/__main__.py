import sys
import argparse

from .lisp import parse, evaluate


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("file",
        type=argparse.FileType(),
        default="-",
        nargs="?")

    args = parser.parse_args()

    for i in parse(args.file):
        evaluate(i)
#    for i in parse(args.file):
#        print(i)


if __name__ == "__main__":
    sys.exit(main())
