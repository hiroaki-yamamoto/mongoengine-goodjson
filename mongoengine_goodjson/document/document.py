#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Document."""

from mongoengine.document import Document as OrigDoc
from .custom import CustomDocumentBase


class Document(CustomDocumentBase, OrigDoc):
    """Base document."""

    meta = {
        "abstract": True,
    }
