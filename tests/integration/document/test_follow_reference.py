#!/usr/bin/env python
# coding=utf-8

"""Document follow reference flag test."""

import json

from ..fixtures.reference import Reference
from ...con_base import DBConBase


class FollowReferenceTest(DBConBase):
    """Good JSON follow reference encoder/decoder test."""

    def setUp(self):
        """Set up function."""
        self.maxDiff = None
        self.reference_cls = Reference
        self.reference = self.reference_cls.generate_test_data()
        self.reference.ex_ref.save()
        for ref in self.reference.ex_refs:
            ref.save()
        self.reference.save()
        self.reference_dict = self.reference.to_dict()

    def test_encode_follow_reference_data(self):
        """Reference data should follow ReferenceField."""
        result = json.loads(self.reference.to_json(follow_reference=True))
        self.assertDictEqual(self.reference_dict, result)

    def test_decode_reference(self):
        """The decoded reference data should be self.reference."""
        result = self.reference_cls.from_json(
            json.dumps(self.reference_dict)
        )
        self.assertIs(type(result), self.reference_cls)
        self.assertEqual(result.id, self.reference.id)
        self.assertEqual(result.name, self.reference.name)
        self.assertListEqual(self.reference.references, result.references)

    def test_actual_data_store(self):
        """Actually data store."""
        for ref in self.reference.references:
            ref.user.save()
            ref.save()
        self.reference.save()
        result = json.loads(
            self.reference_cls.objects(
                id=self.reference.id
            ).get().to_json(follow_reference=True)
        )
        self.assertDictEqual(self.reference_dict, result)
