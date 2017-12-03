import itertools as it
import functools as fc

from ..utils import fstr
from .core import atom, MaxeExpression, MaxeSymbol


def plus(first, *rest):
    return fc.reduce(lambda a, b: a + b, rest, first)


def minus(first, *rest):
    return fc.reduce(lambda a, b: b - a, rest, 0)


def multiply(first, *rest):
    return fc.reduce(lambda a, b: a * b, rest, first)


def divide(first, *rest):
    return fc.reduce(lambda a, b: a / b, rest, first)


def exponent(first, *rest):
    return first ** fc.reduce(lambda a, b: b**a, reversed(rest), 1)


core_env = {
    atom("+"): plus,
    atom("-"): minus,
    atom("*"): multiply,
    atom("/"): divide,
    atom("**"): exponent,
    atom("^"): exponent,
    atom("print"): lambda *s: print(*s),
    atom("format"): fstr,
    atom("car"): lambda x: x[0],
    atom("cdr"): lambda x: x[1:],
}


def evaluate(ast, env=None):
    if env is None:
        env = core_env

    if isinstance(ast, MaxeSymbol):
        return env[ast]
    # number or string
    elif not isinstance(ast, MaxeExpression):
        return ast

    op = ast[0]
    args = ast[1:]

    if op == atom("quote"):
        return args[0]

    proc = evaluate(op, env)
    vals = [evaluate(arg, env) for arg in args]
    return proc(*vals)
