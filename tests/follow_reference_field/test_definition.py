#!/usr/bin/env python
# coding=utf-8

"""FollowReferenceFieldTest specs."""

from unittest import TestCase
import mongoengine_goodjson as gj
import mongoengine as db


class FolowReferenceFieldDefinitionTest(TestCase):
    """Follow Reference Field should be defined."""

    def test_definition(self):
        """Follow Reference Field should inherit BaseField."""
        self.assertTrue(
            issubclass(gj.FollowReferenceField, db.ReferenceField)
        )
