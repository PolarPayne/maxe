import io
import re
from enum import Enum

from .core import atom, MaxeExpression
from ..utils import fstr, ferr, FileCharIter

WHITESPACE = (" ", "\t", "\n")


class State(Enum):
    other = 0
    in_str = 1
    in_comment = 2


def parse(fp):
    line = 1
    column = 0

    depth = 0

    state = State.other
    skip_next = False

    stack = MaxeExpression(MaxeExpression())
    ident = []

    def handle_ident():
        nonlocal ident

        if ident:
            stack.peek().append(atom("".join(ident)))
            ident = []

        while len(stack.peek()) >= 1 and stack.peek()[0] == atom("quote"):
            tmp = stack.pop()
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
        if state is State.in_comment and char == "\\":
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
        elif state is State.in_str and char != '"':
            ident.append(char)

        # --- no longer inside a string ---

        # inside a comment
        elif state is State.in_comment:
            if char == "\n":
                state = ""

        # whitespace
        elif char in WHITESPACE:
            state = ""
            handle_ident()

        # start or end of string
        elif char == '"':
            if state is State.in_str:
                state = ""
            elif state is "":
                state = State.in_str
            else:
                # TODO fail
                ferr("'\"' in an invalid place at {}:{}", line, column)
            ident.append(char)

        # start of comment
        elif char == ";":
            state = State.in_comment

        elif char == "'":
            handle_ident()
            stack.append(MaxeExpression(atom("quote")))

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
