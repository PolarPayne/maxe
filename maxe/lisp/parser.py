import io
import re
from collections import deque

from ..utils import fstr, ferr, FileCharIter

INT_RE = re.compile(r"^[+-]?[0-9]+[0-9,_]*([eE][+-]?[0-9]+[0-9,_]*)?$")
FLOAT_RE = re.compile(r"^[+-]?([0-9]+[0-9,_]*)?\.[0-9]+[0-9_,]*([eE][+-]?[0-9]+[0-9,_]*)?$")


class MaxeString:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return fstr('"{}"', self.value.replace('"', '\\"'))

    def __repr__(self):
        return fstr("<MaxeString {}>", str(self))


class MaxeFloat(float): pass


class MaxeInt(int): pass


class MaxeSymbol(str):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def __repr__(self):
        return fstr("<MaxeSymbol {}>", str(self))

    def __eq__(self, other):
        if type(other) is not self.__class__:
            return False
        return self.value == other.value


class MaxeExpression:
    def __init__(self, *values):
        self.values = deque(values)

    def append(self, value):
        self.values.append(value)

    def pop(self):
        return self.values.pop()

    def peek(self):
        return self.values[-1]

    def peek_bottom(self):
        return self.values[0]

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        yield from self.values

    def __str__(self):
        return fstr("({})", " ".join(map(str, self)))

    def __repr__(self):
        return fstr("<MaxeExpression ({})>", " ".join(map(repr, self)))


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


def parse_file(fp):
    line = 1
    column = 0

    depth = 0

    WHITESPACE = (" ", "\t", "\n")
    state = ""
    skip_next = False

    stack = MaxeExpression(MaxeExpression())
    ident = []

    def handle_ident():
        nonlocal ident

        if ident:
            stack.peek().append(atom("".join(ident)))
            ident = []

        while len(stack.peek()) >= 1 and stack.peek().peek_bottom() == MaxeSymbol("quote"):
            tmp = stack.pop()
            print("> quote", stack.peek())
            stack.peek().append(tmp)

    for char, lookahead in FileCharIter(fp):
        column += 1

        if char == "\n":
            line += 1
            column = 0

        if skip_next:
            skip_next = False
            continue

        # string escaping
        if state == "in_str" and char == "\\":
            if lookahead == "n":
                char = "\n"
                skip_next = True
            elif lookahead == "t":
                char = "\t"
                skip_next = True
            elif lookahead == '"':
                char = '"'
                skip_next = True
            elif lookahead == "\\":
                char = "\\"
                skip_next = True
            elif lookahead == "\n":
                char = ""
                skip_next = True
            ident.append(char)

        # normal character in string
        elif state == "in_str" and char != '"':
            ident.append(char)

        # --- no longer inside a string ---

        # inside a comment
        elif state == "in_comment":
            if char == "\n":
                state = ""

        # whitespace
        elif char in WHITESPACE:
            state = ""
            handle_ident()

        # start or end of string
        elif char == '"':
            if state == "in_str":
                state = ""
            elif state == "":
                state = "in_str"
            else:
                # TODO fail
                ferr("'\"' in an invalid place at {}:{}", line, column)
            ident.append(char)

        # start of comment
        elif char == ";":
            state = "in_comment"

        # TODO transform '(a b c) to (quote (a b c))
        elif char == "'":
            handle_ident()
            stack.append(MaxeExpression(MaxeSymbol("quote")))

        # open bracket
        elif char == "(":
            depth += 1
            stack.append(MaxeExpression())
            handle_ident()

        # close bracket
        elif char == ")":
            depth -= 1
            handle_ident()
            tmp = stack.pop()
            stack.peek().append(tmp)

        # everything else must be characters
        else:
            ident.append(char)

        if depth < 0:
            ferr("extra closing bracket ')' at {}:{}", line, column)
    if depth > 0:
        ferr("missing closing bracket ')'")

    assert len(stack) == 1, fstr("""\
stack should have had only single item left, but it had {}
stack:
{}""", len(stack), "\n".join(map(lambda s: "  " + str(s), stack)))
    return stack.pop()
