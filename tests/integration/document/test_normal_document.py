#!/usr/bin/env python
# coding=utf-8

"""Test normal document."""

from calendar import timegm
import json
from six import text_type

from ..fixtures.articles import Article
from ..fixtures.user import User
from ...con_base import DBConBase


class NormalDocumentTest(DBConBase):
    """Good JSON Encoder / Decoder Normal Data test."""

    def setUp(self):
        """Set up the class."""
        self.maxDiff = None
        self.user_cls = User
        self.user = self.user_cls.generate_test_data()
        self.article_cls = Article
        self.article = self.article_cls.generate_test_data(user=self.user)
        self.user_dict = self.user.to_dict()
        self.article_dict = self.article.to_dict()
        self.article_ref_fld_dict = self.article_dict.copy()
        self.article_dict["user"] = text_type(self.user.id)
        self.article_dict_epoch = self.article_dict.copy()
        self.article_dict_epoch["date"] = int(
            (timegm(self.article.date.timetuple()) * 1000) +
            (self.article.date.microsecond / 1000)
        )

    def test_encode_user_data(self):
        """User model should be encoded properly."""
        result = json.loads(self.user.to_json())
        self.assertEqual(self.user_dict, result)

    def test_encode_article_data(self):
        """Article model should be encoded properly."""
        result = json.loads(self.article.to_json())
        self.assertEqual(self.article_dict, result)

    def test_encode_article_data_epoch_flag(self):
        """Article model should be encoded properly (Epoch flag is on)."""
        result = json.loads(self.article.to_json(epoch_mode=True))
        self.assertEqual(self.article_dict_epoch, result)

    def test_decode_user_data(self):
        """The decoded user data should be self.user."""
        user = self.user_cls.from_json(json.dumps(self.user_dict))
        self.assertIs(type(user), self.user_cls)
        self.assertEqual(self.user.to_mongo(), user.to_mongo())

    def test_decode_article_data(self):
        """The decoded user data should be self.user."""
        article = self.article_cls.from_json(json.dumps(self.article_dict))
        self.assertIs(type(article), self.article_cls)
        self.assertEqual(self.article.to_mongo(), article.to_mongo())

    def test_decode_article_data_epoch(self):
        """The decoded user data should be self.article."""
        article = self.article_cls.from_json(
            json.dumps(self.article_dict_epoch)
        )
        self.assertIs(type(article), self.article_cls)
        self.assertEqual(self.article.to_mongo(), article.to_mongo())

    def test_normal_follow_reference(self):
        """The to_json(follow_reference=True) should follow the reference."""
        self.assertEqual(
            json.loads(self.article.to_json(follow_reference=True)),
            self.article_ref_fld_dict
        )
