import itertools as it
import functools as fc

from ..utils import fstr
from .core import atom, MaxeExpression, MaxeSymbol


def plus(*args):
    return fc.reduce(lambda a, b: a + b, args, 0)


def minus(*args):
    return fc.reduce(lambda a, b: b - a, args, 0)


core_env = {
    atom("+"): plus,
    atom("-"): minus,
    atom("print"): print,
    atom("format"): fstr,
    atom("car"): lambda args: args[0],
    atom("cdr"): lambda args: args[1:],
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
