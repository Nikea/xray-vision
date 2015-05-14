import matplotlib
import matplotlib.pyplot as plt
from functools import wraps


def ensure_ax(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'ax' in kwargs:
            ax = kwargs.pop('ax', None)
        elif len(args) > 0 and isinstance(args[0], matplotlib.axes.Axes):
            ax = args[0]
            args = args[1:]
        else:
            ax = plt.gca()
        return func(ax, *args, **kwargs)
    return inner


def ensure_ax_meth(func):

    @wraps(func)
    def inner(*args, **kwargs):
        s = args[0]
        args = args[1:]
        if 'ax' in kwargs:
            ax = kwargs.pop('ax', None)
        elif len(args) > 1 and isinstance(args[0], matplotlib.axes.Axes):
            ax = args[0]
            args = args[1:]
        else:
            ax = plt.gca()
        return func(s, ax, *args, **kwargs)
    return inner
