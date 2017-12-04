import itertools as it
import functools as fc

from ..utils import fstr
from .core import atom, MaxeExpression, MaxeSymbol


def plus(first, *rest):
    return fc.reduce(lambda a, b: a + b, rest, first)


def minus(first, *rest):
    return first + fc.reduce(lambda a, b: a - b, rest, 0)


def multiply(first, *rest):
    return fc.reduce(lambda a, b: a * b, rest, first)


def divide(first, *rest):
    return fc.reduce(lambda a, b: a / b, rest, first)


def exponent(first, *rest):
    return first ** fc.reduce(lambda a, b: b**a, reversed(rest), 1)


QUOTE = atom("quote")
DEFINE = atom("define")
LET = atom("let")
LET_STAR = atom("let*")
CORE_ENV = {
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
        env = CORE_ENV
    env_copy = env.copy()

    if isinstance(ast, MaxeSymbol):
        return env[ast]
    # number or string
    elif not isinstance(ast, MaxeExpression):
        return ast

    op = ast[0]
    args = ast[1:]

    if op == QUOTE:
        return args[0]
    elif op == DEFINE:
        env[args[0]] = evaluate(args[1], env)
        return MaxeExpression()
    elif op == LET:
        env_copy[args[0][0]] = evaluate(args[0][1], env)
        return evaluate(args[1], env_copy)
    elif op == LET_STAR:
        for i in args[0:-1]:
            env_copy[i[0]] = evaluate(i[1], env_copy)
        return evaluate(args[-1], env_copy)

    else:
        proc = evaluate(op, env)
        while not callable(proc):
            proc = evaluate(proc, env)
        vals = [evaluate(arg, env) for arg in args]
        return proc(*vals)
