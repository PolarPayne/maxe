import io

from .core import MaxeAtom, MaxeExpression
from ..utils import fstr, ferr, FileCharIter


def parse_file(fp):
    line = 1
    column = 0

    depth = 0

    WHITESPACE = (" ", "\t", "\n")
    state = ""
    skip_next = False

    out = MaxeExpression()
    ast = []
    ident = []

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
            if ident:
                ast[-1].add(MaxeAtom("".join(ident)))
                ident = []

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

        # open bracket
        elif char == "(":
            if ident:
                ast[-1].add(MaxeAtom("".join(ident)))
                ident = []
            depth += 1
            ast.append(MaxeExpression())

        # close bracket
        elif char == ")":
            if ident:
                ast[-1].add(MaxeAtom("".join(ident)))
                ident = []
            depth -= 1
            tmp = ast.pop()
            if ast:
                ast[-1].add(tmp)
            else:
                out.add(tmp)

        # everything else must be characters
        else:
            ident.append(char)

        if depth < 0:
            ferr("extra closing bracket ')' at {}:{}", line, column)
    if depth > 0:
        ferr("missing closing bracket ')'")

    return out
