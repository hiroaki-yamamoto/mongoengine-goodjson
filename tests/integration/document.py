#!/usr/bin/env python
# coding=utf-8

"""Integration tests."""

import json
from unittest import TestCase

from .schema import User, Article, Email
from .fixtures import (
    user, user_dict, article, article_dict,
    email, email_dict_id, email_dict_email
)

try:
    str = unicode
except NameError:
    pass


class ToJSONNormalIntegrationTest(TestCase):
    """Good JSON Encoder Normal Data test."""

    def setUp(self):
        """Setup the class."""
        self.maxDiff = None
        self.user_cls = User
        self.user = user
        self.article_cls = Article
        self.article = article
        self.user_dict = user_dict
        self.article_dict = article_dict

    def test_encode_user_data(self):
        """User model should be encoded properly."""
        result = json.loads(self.user.to_json())
        self.assertDictEqual(self.user_dict, result)

    def test_encode_article_data(self):
        """Article model should be encoded properly."""
        result = json.loads(self.article.to_json())
        self.assertDictEqual(self.article_dict, result)

    def test_decode_user_data(self):
        """The decoded user data should be self.ser."""
        user = self.user_cls.from_json(json.dumps(self.user_dict))
        self.assertIs(type(user), self.user_cls)
        self.assertDictEqual(self.user.to_mongo(), user.to_mongo())

    def test_decode_article_data(self):
        """The decoded user data should be self.expected_user."""
        article = self.article_cls.from_json(json.dumps(self.article_dict))
        self.assertIs(type(article), self.article_cls)
        self.assertDictEqual(self.article.to_mongo(), article.to_mongo())


class PrimaryKeyNotOidTest(TestCase):
    """Good JSON encoder/decoder email as primary key test."""

    def setUp(self):
        """Setup the class."""
        self.email = email
        self.data_id = email_dict_id
        self.data_email = email_dict_email

    def test_encode(self):
        """Email document should be encoded properly."""
        result = json.loads(self.email.to_json())
        self.assertDictEqual(self.data_id, result)

    def test_decode_id(self):
        """
        Email document should be decoded from json properly.

        This test is in the case that email is at "id" field.
        """
        result = Email.from_json(json.dumps(self.data_id)).to_mongo()
        self.assertDictEqual(self.email.to_mongo(), result)

    def test_decode_email(self):
        """
        Email document should be decoded from json properly.

        This test is in the case that email is at "email" field.
        """
        result = Email.from_json(json.dumps(self.data_email)).to_mongo()
        self.assertDictEqual(self.email.to_mongo(), result)
