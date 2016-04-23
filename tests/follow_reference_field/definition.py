#!/usr/bin/env python
# coding=utf-8

"""FollowReferenceFieldTest specs."""

from unittest import TestCase
import mongoengine_goodjson as gj
import mongoengine as db


class FolowReferenceFieldDefinitionTest(TestCase):
    """FollowReferenceField should be defined."""

    def test_definition(self):
        """FollowReferenceField should inherit BaseField."""
        self.assertTrue(
            issubclass(gj.FollowReferenceField, db.ReferenceField)
        )
