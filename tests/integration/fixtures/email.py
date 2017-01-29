#!/usr/bin/env python
# coding=utf-8

"""Email."""

from six import text_type

import mongoengine as db
import mongoengine_goodjson as gj
from .base import Dictable


class Email(Dictable, gj.Document):
    """Test schema."""

    email = db.EmailField(primary_key=True)

    @classmethod
    def generate_test_data(cls):
        """Generate test data."""
        return cls(email="test@example.com")

    def to_dict(self):
        """Convert into dict."""
        return {text_type("id"): self.pk}
