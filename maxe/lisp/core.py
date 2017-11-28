import re

from ..utils import fstr

INT_RE = re.compile(r"^[+-]?[0-9]+[0-9,_]*([eE][+-]?[0-9]+[0-9,_]*)?$")
FLOAT_RE = re.compile(r"^[+-]?([0-9]+[0-9,_]*)?\.[0-9]+[0-9_,]*([eE][+-]?[0-9]+[0-9,_]*)?$")


def MaxeAtom(s):
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return MaxeString(s[1:-1])
    if INT_RE.match(s):
        return MaxeInt(s)
    if FLOAT_RE.match(s):
        return MaxeFloat(s)
    return MaxeSymbol(s)


class MaxeSymbol:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return fstr("{}", self.value)


def proc_number(s):
    s = (s
        .replace(",", "")
        .replace("_", "")
        .replace("+", "")
        .replace("E", "e")
        .split("e"))
    assert(1 <= len(s) <= 2)
    return s[0], int(s[1]) if len(s) == 2 else 0


class MaxeInt:
    def __init__(self, value):
        value, exponent = proc_number(value)
        self.value = int(value) * 10**exponent

    def __str__(self):
        return fstr("{}i", self.value)


class MaxeFloat:
    def __init__(self, value):
        value, exponent = proc_number(value)
        self.value = float(value) * 10**exponent

    def __str__(self):
        return fstr("{}f", self.value)


class MaxeString:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return fstr('"{}"', self.value)


class MaxeExpression:
    def __init__(self, children=None):
        self.children = children
        if children is None:
            self.children = []

    def add(self, value):
        self.children.append(value)

    def __len__(self):
        return len(self.children)

    def __str__(self):
        return fstr("({})", " ".join(map(str, self.children)))
