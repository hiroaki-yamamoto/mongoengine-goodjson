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
    wrapper.dispatch = dispatcher.dispatch
    update_wrapper(wrapper, func)
    return wrapper


@singledispatch
def normalize_reference(ref_id, fld):
    """Normalize Reference."""
    return ref_id and fld.to_python(ref_id) or None


@normalize_reference.register(dict)
def normalize_reference_dict(ref_id, fld):
    """Normalize Reference for dict."""
    return fld.to_python(ref_id.get("id") or ref_id["_id"])


@normalize_reference.register(list)
def normalize_reference_list(ref_id, fld):
    """Normalize Reference for list."""
    return [normalize_reference(ref.id, fld) for ref in ref_id]
