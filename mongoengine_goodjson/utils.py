#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utility functions."""

from functools import update_wrapper
import collections as cl

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
    # If fld has a "to_python" method (which should always be the case), call
    # it. Else, simply use the value as is.
    fld_to_python = getattr(fld, "to_python", lambda: fld)(ref_id)
    return ref_id and fld_to_python or None


@normalize_reference.register(dict)
def normalize_reference_dict(ref_id, fld):
    """Normalize Reference for dict."""
    return fld.to_python(ref_id.get("id") or ref_id["_id"])


@normalize_reference.register(list)
def normalize_reference_list(ref_id, fld):
    """Normalize Reference for list."""
    return [normalize_reference(ref.id, fld) for ref in ref_id]


def id_first(dct):
    """
    Return dict that comes id first.

    Note that this func returns dct as it is if "id" is not found in dct.

    """

    if "id" in list(dct.keys()):
        items = [("id", dct.pop("id"))]
        items.extend(dct.items())
        return cl.OrderedDict(items)
    else:
        return dct
