#!/usr/bin/env python
# coding=utf-8

"""Field exclusion tests."""

from datetime import datetime
import json

from bson import ObjectId
import mongoengine_goodjson as gj
import mongoengine as db

from ...con_base import DBConBase
from ..fixtures.base import Dictable


class JSONExclusionTest(DBConBase):
    """JSON Exclusion Test."""

    def setUp(self):
        """Setup."""
        class ExclusionModel(gj.Document):
            to_json_exclude = db.StringField(exclude_to_json=True)
            from_json_exclude = db.IntField(exclude_from_json=True)
            json_exclude = db.StringField(exclude_json=True)
            required = db.StringField(required=True)

        self.cls = ExclusionModel
        self.data = {
            "to_json_exclude": "Hello",
            "from_json_exclude": 10234,
            "json_exclude": "Hi",
            "required": "World"
        }
        self.model = self.cls(**self.data)

    def test_to_json(self):
        """to_json_exclude and json_exclude shouldn't be in the output data."""
        result = json.loads(self.model.to_json())
        self.assertNotIn("to_json_exclude", result)
        self.assertNotIn("json_exclude", result)
        self.assertIn("from_json_exclude", result)
        self.assertIn("required", result)

    def test_from_json(self):
        """from_json_exclude and json_exclude shouldn't be decoded."""
        result = self.cls.from_json(json.dumps(self.data))
        self.assertIsNone(result.from_json_exclude)
        self.assertIsNone(result.json_exclude)
        self.assertIsNotNone(result.to_json_exclude)
        self.assertIsNotNone(result.required)


class EmbeddedDocumentJsonExclusionTest(DBConBase):
    """Complex JSON exclusion test."""

    @classmethod
    def setUpClass(cls):
        """Set up class."""
        super(EmbeddedDocumentJsonExclusionTest, cls).setUpClass()

        class CheckObj(object):
            def check(self, input_data):
                for (name, fld) in self._fields.items():
                    value = getattr(self, name, None)
                    if getattr(fld, "exclude_from_json", None):
                        if isinstance(value, list):
                            assert len(value) == 0, (
                                "{} is not emtpy: {}"
                            ).format(name, value)
                        else:
                            assert value is None, (
                                "{} is not None: {}"
                            ).format(name, value)
                    elif hasattr(value, "check"):
                        value.check(input_data[name])
                    elif isinstance(value, list):
                        for index, item in enumerate(getattr(self, name)):
                            item.check(input_data[name][index])
                    else:
                        assert value == fld.to_python(
                            input_data[name]
                        ), ("{} is not {}: {}").format(
                            name, input_data[name], getattr(self, name)
                        )

        class EmbDoc(CheckObj, Dictable, gj.EmbeddedDocument):
            name = db.StringField()
            meta_id = db.ObjectIdField(exclude_json=True)
            description = db.StringField(exclude_form_json=True)
            public_date = db.DateTimeField(exclude_to_json=True)

            @classmethod
            def generate_test_data(cls, prefix="", suffix=""):
                return cls(
                    name=("{}Test{}").format(prefix, suffix),
                    meta_id=ObjectId(),
                    description=(
                        "{}Test Description{}"
                    ).format(prefix, suffix),
                    public_date=datetime.utcnow()
                )

        class ComplexExclusionModel(CheckObj, Dictable, gj.Document):
            emb_docs_ex_to_json = db.ListField(
                db.EmbeddedDocumentField(EmbDoc), exclude_to_json=True
            )
            emb_docs_ex_from_json = db.ListField(
                db.EmbeddedDocumentField(EmbDoc), exclude_from_json=True
            )
            emb_docs_ex_json = db.ListField(
                db.EmbeddedDocumentField(EmbDoc), exclude_json=True
            )
            emb_doc = db.EmbeddedDocumentField(EmbDoc)

            @classmethod
            def generate_test_data(cls, prefix="", suffix=""):
                return cls(
                    emb_docs_ex_to_json=[
                        EmbDoc.generate_test_data(
                            prefix=(
                                "{} (emb_docs_ex_to_json) "
                            ).format(prefix),
                            suffix=("{} {}").format(suffix, counter)
                        ) for counter in range(3)
                    ],
                    emb_docs_ex_from_json=[
                        EmbDoc.generate_test_data(
                            prefix=(
                                "{} (emb_docs_ex_from_json) "
                            ).format(prefix),
                            suffix=("{} {}").format(suffix, counter)
                        ) for counter in range(3)
                    ],
                    emb_docs_ex_json=[
                        EmbDoc.generate_test_data(
                            prefix=("{} (emb_docs_ex_json) ").format(prefix),
                            suffix=("{} {}").format(suffix, counter)
                        ) for counter in range(3)
                    ],
                    emb_doc=EmbDoc.generate_test_data(
                        prefix=("{} (emb_dos) ").format(prefix),
                        suffix=("{}").format(suffix)
                    )
                )
        cls.doc_cls = ComplexExclusionModel

    def setUp(self):
        """Setup."""
        self.doc = self.doc_cls.generate_test_data()
        self.doc.save()

    def tearDown(self):
        """Tear down."""
        self.doc_cls.drop_collection()

    def test_to_json(self):
        """Test to_json."""
        result = json.loads(self.doc.to_json())
        correct = self.doc.to_dict()
        correct.pop("emb_docs_ex_to_json")
        correct.pop("emb_docs_ex_json")
        correct["emb_docs_ex_from_json"] = [
            {
                key: value
                for (key, value) in item.items()
                if key != "meta_id" and key != "public_date"
            } for item in correct["emb_docs_ex_from_json"]
        ]
        correct["emb_doc"].pop("meta_id")
        correct["emb_doc"].pop("public_date")
        self.assertEqual(result, correct)

    def test_from_json(self):
        """Test from_json."""
        data = self.doc.to_dict()
        obj = self.doc_cls.from_json(json.dumps(data))
        obj.check(data)
