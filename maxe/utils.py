import sys
import io


def fstr(s, *args, **kwargs):
    return str(s).format(*args, **kwargs)


def fout(s, *args, **kwargs):
    print(fstr(s, *args, **kwargs))


def ferr(s, *args, **kwargs):
    print(fstr(s, *args, **kwargs), file=sys.stderr)


class FileCharIter:
    """
    Iterate through a file efficiently character by character
    (with one character lookahead).
    """

    def __init__(self, fp):
        self.fp = fp
        self.chunk = ""

    def __iter__(self):
        return self

    def __next__(self):
        if not self.chunk:
            self.chunk = self.fp.read(io.DEFAULT_BUFFER_SIZE)
        if not self.chunk:
            raise StopIteration()
        if len(self.chunk) < 2:
            self.chunk += self.fp.read(io.DEFAULT_BUFFER_SIZE)

        if len(self.chunk) < 2:
            char, lookahead = self.chunk[0], None
        else:
            char, lookahead = self.chunk[0], self.chunk[1]

        self.chunk = self.chunk[1:]
        return char, lookahead


if __name__ == "__main__":
    with open("./design.txt") as fp:
        for a, b in FileCharIter(fp):
            print(a, "---", b)