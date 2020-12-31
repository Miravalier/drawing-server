import sys


class FatalException(Exception):
    pass


def debug(*args, **kwargs):
    print("\x1B[35m[!]\x1B[0m", *args, file=sys.stderr, **kwargs)


def success(*args, **kwargs):
    print("\x1B[92m[!]\x1B[0m", *args, file=sys.stderr, **kwargs)


def error(*args, **kwargs):
    print("\x1B[31m[!]\x1B[0m", *args, file=sys.stderr, **kwargs)


def info(*args, **kwargs):
    print("\x1B[0m[.]\x1B[0m", *args, file=sys.stderr, **kwargs)


def fatal(*args, sep=" ", end="\n"):
    raise FatalException(sep.join(args) + end)
