from .utils import fstr, ferr


class Atom:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return fstr("<{}>", self.value)


class SExpression:
    def __init__(self, children=None):
        self.children = children
        if children is None:
            self.children = []

    def add(self, value):
        self.children.append(value)

    def __len__(self):
        return len(self.children)

    def __repr__(self):
        return fstr("[{}]", ", ".join(map(str, self.children)))


def proc_file(file: str) -> None:
    with open(file) as f:
        data = f.read()

    line = 1
    column = 0

    depth = 0

    WHITESPACE = (" ", "\t", "\n")
    state = ""
    lookahead = ""
    skip_next = False

    out = SExpression()
    ast = []
    ident = []

    for i, char in enumerate(data):
        column += 1

        if char == "\n":
            line += 1
            column = 0

        if data[i+1:]:
            lookahead = data[i+1]
        else:
            lookahead = ""

        if skip_next:
            skip_next = False
            continue

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
        elif state == "in_str" and char != '"':
            ident.append(char)

        elif state == "in_ident":
            ident.append(char)

        elif char == "(":
            if ident:
                ast[-1].add(Atom("".join(ident)))
                ident = []
            depth += 1
            ast.append(SExpression())

        elif char == ")":
            if ident:
                ast[-1].add(Atom("".join(ident)))
                ident = []
            depth -= 1
            tmp = ast.pop()
            if ast:
                ast[-1].add(tmp)
            else:
                out.add(tmp)

        elif char == '"':
            if state == "in_str":
                state = ""
            elif state == "":
                state = "in_str"

        elif char in WHITESPACE:
            if ident:
                ast[-1].add(Atom("".join(ident)))
                ident = []

        # everything else must be characters
        else:
            ident.append(char)

        if depth < 0:
            ferr("extra closing bracket ')' at {}:{}", line, column)
    if depth > 0:
        ferr("missing closing bracket ')'")

    return out
