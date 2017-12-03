import re

from ..utils import fstr

INT_RE = re.compile(r"^[+-]?[0-9]+[0-9,_]*([eE][+-]?[0-9]+[0-9,_]*)?$")
FLOAT_RE = re.compile(r"^[+-]?([0-9]+[0-9,_]*)?\.[0-9]+[0-9_,]*([eE][+-]?[0-9]+[0-9,_]*)?$")


class MaxeString:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return fstr("{}", self.value)

    def __repr__(self):
        return fstr('"{}"', self.value.replace('"', '\\"'))


class MaxeFloat(float):
    pass


class MaxeInt(int):
    pass


class MaxeSymbol(str):
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return self.value

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if type(other) is not self.__class__:
            return False
        return self.value == other.value


class MaxeExpression:
    def __init__(self, *values):
        self.values = list(values)

    def append(self, value):
        self.values.append(value)

    def pop(self):
        return self.values.pop()

    def peek(self):
        return self.values[-1]

    def __getitem__(self, index):
        if type(index) is slice:
            return MaxeExpression(*self.values[index])
        return self.values[index]

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        yield from self.values

    def __str__(self):
        return fstr("({})", " ".join(map(repr, self)))

    def __repr__(self):
        return str(self)


def proc_number(s):
    s = (s
        .replace(",", "")
        .replace("_", "")
        .replace("+", "")
        .replace("E", "e")
        .split("e"))
    assert(1 <= len(s) <= 2)
    return s[0], int(s[1]) if len(s) == 2 else 0


def atom(s):
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return MaxeString(s[1:-1])
    if INT_RE.match(s):
        value, exp = proc_number(s)
        return MaxeInt(int(value) * 10**exp)
    if FLOAT_RE.match(s):
        value, exp = proc_number(s)
        return MaxeFloat(float(value) * 10**exp)
    return MaxeSymbol(s)
