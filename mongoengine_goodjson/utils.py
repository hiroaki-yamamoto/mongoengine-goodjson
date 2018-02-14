#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utility functions."""

from functools import update_wrapper

try:
    from functools import singledispatch
except ImportError:
    from singledispatch import singledispatch


def method_dispatch(func):
    """Dispatch class instance method with functools.singledispatch."""
    # Note thanks for Zero Piraeus at Stackoverflow:
    # https://stackoverflow.com/questions/24601722/how-can-i-use-functools-singledispatch-with-instance-methods
    dispatcher = singledispatch(func)

    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)

    wrapper.register = dispatcher.register
    update_wrapper(wrapper, func)
    return wrapper
