#!/usr/bin/env python
# coding=utf-8

"""Document follow reference flag test."""

from collections import OrderedDict
import json

try:
    from unittest.mock import MagicMock, call
except ImportError:
    from mock import MagicMock, call

import mongoengine as db
import mongoengine_goodjson as gj

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
        for dct_ref in self.reference.ex_dict.values():
            dct_ref.save()
        self.reference.save()
        self.reference_dict = self.reference.to_dict()

    def test_encode_follow_reference_data(self):
        """Reference data should follow ReferenceField."""
        result = json.loads(
            self.reference.to_json(follow_reference=True),
            object_pairs_hook=OrderedDict
        )
        self.assertEqual(
            list(result.items())[0][0], 'id',
            'The key of the first element must be "id".'
        )
        self.assertEqual(self.reference_dict, result)

    def test_decode_reference(self):
        """The decoded reference data should be self.reference."""
        result = self.reference_cls.from_json(
            json.dumps(self.reference_dict)
        )
        self.assertIs(type(result), self.reference_cls)
        self.assertEqual(result.id, self.reference.id)
        self.assertEqual(result.name, self.reference.name)
        self.assertEqual(self.reference.references, result.references)
        self.assertEqual(
            self.reference.ex_dict, result.ex_dict
        )

    def test_serialize_deserialize_reference(self):
        """The data after serialization and deserialization should be exactly
        the same"""
        result = self.reference.to_json(follow_reference=True)

        result = self.reference_cls.from_json(result)

        resultDict = result.to_dict()

        self.assertEqual(self.reference_dict, resultDict)

    def test_save_deserialized_reference(self):
        """The deserialized data should be saved correctly in the database"""
        result = self.reference_cls.from_json(
            json.dumps(self.reference_dict)
        )

        result.save()
        savedResult = json.loads(
            self.reference_cls.objects(
                id=self.reference.id
            ).get().to_json(follow_reference=True)
        )
        self.assertDictEqual(self.reference_dict, savedResult)

    def test_deserialize_without_id(self):
        """Id fields are not necessary in JSON files"""

        def remove_ids(d, new_dict):
            # Recursively remove all id fields in the dictionary
            for k, v in d.items():
                if isinstance(v, dict):
                    new_dict[k] = {}
                    remove_ids(v, new_dict[k])
                elif isinstance(v, list):
                    new_dict[k] = []
                    for item in v:
                        if isinstance(item, dict):
                            new_dict[k].append({})
                            remove_ids(item, new_dict[k][-1])
                        else:
                            new_dict[k].append(item)
                else:
                    if k != 'id':
                        new_dict[k] = v

        reference_dict_no_id = {}
        remove_ids(self.reference_dict, reference_dict_no_id)

        result = self.reference_cls.from_json(
            json.dumps(reference_dict_no_id)
        )
        result.save()
        savedResult = json.loads(
            self.reference_cls.objects(
                id=result.id
            ).get().to_json(follow_reference=True)
        )

        resultDict_no_id = {}
        remove_ids(savedResult, resultDict_no_id)

        self.assertDictEqual(reference_dict_no_id, resultDict_no_id)

    def test_actual_data_store(self):
        """Actually data store."""
        for ref in self.reference.references:
            ref.user.save()
            ref.save()
        for ref in self.reference.dict_references.values():
            ref.user.save()
            ref.save()
        self.reference.save()
        result = json.loads(
            self.reference_cls.objects(
                id=self.reference.id
            ).get().to_json(follow_reference=True)
        )
        self.assertDictEqual(self.reference_dict, result)


class CallableRecursionTest(DBConBase):
    """Callable recursion test."""

    def setUp(self):
        """Setup."""
        super(CallableRecursionTest, self).setUp()
        self.check_depth = MagicMock(
            side_effect=lambda doc, cur_depth: doc.is_last
        )

        class TestDoc(gj.Document):
            """Test document."""

            name = db.StringField()
            is_last = db.BooleanField()
            ref = db.ReferenceField("self")

            def __str__(self):
                """Return stringified summary."""
                return ("TestDoc<ID: {}, is_last: {}, ref: {}>").format(
                    self.name, self.is_last, getattr(self.ref, "id", None)
                )

            def to_dict(self):
                """Return the dict."""
                return {
                    "id": str(self.id),
                    "name": self.name,
                    "is_last": self.is_last,
                    "ref": (
                        str(self.ref.id) if self.is_last
                        else self.ref.to_dict()
                    )
                }

        self.docs = [
            TestDoc.objects.create(
                name=("Test {}").format(count),
                is_last=(count == 4)
            ) for count in range(6)
        ]
        for (index, doc) in enumerate(self.docs):
            doc.ref = self.docs[(index + 1) % len(self.docs)]
            doc.save()

        # Needs to reset mock because doc.save calls to_mongo
        self.check_depth.reset_mock()

    def test_from_first(self):
        """Should encode the element from first to the element is_last=True."""
        max_depth_level = 4
        correct_data = self.docs[0].to_dict()
        actual_data = json.loads(
            self.docs[0].to_json(
                follow_reference=True, max_depth=self.check_depth
            )
        )

        self.maxDiff = None
        self.assertEqual(correct_data, actual_data)
        self.assertEqual(self.check_depth.call_count, max_depth_level + 1)
        self.check_depth.assert_has_calls([
            call(self.docs[count], count)
            for count in range(1, max_depth_level)
        ])
