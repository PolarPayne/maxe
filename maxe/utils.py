import sys


def fstr(s, *args, **kwargs):
    return s.format(*args, **kwargs)


def fout(s, *args, **kwargs):
    print(fstr(s, *args, **kwargs))


def ferr(s, *args, **kwargs):
    print(fstr(s, *args, **kwargs), file=sys.stderr)
