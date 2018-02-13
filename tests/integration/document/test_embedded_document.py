#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test Embedded Document."""

from six import text_type
from calendar import timegm

from .test_normal_document import NormalDocumentTest


# Because the test case that has a normal embedded document is tested in
# NormalDocumentTest, Existing Embedded Document test case will be omitted.


class TestEmbeddedDocumentNoneTest(NormalDocumentTest):
    """Check the behav when embdoc is None."""

    def setUp(self):
        """Setup."""
        super(TestEmbeddedDocumentNoneTest, self).setUp()
        self.article.addition = None
        self.article_dict = self.article.to_dict()
        self.article_ref_fld_dict = self.article_dict.copy()
        self.article_dict["user"] = text_type(self.user.id)
        self.article_dict_epoch = self.article_dict.copy()
        self.article_dict_epoch["date"] = int(
            (timegm(self.article.date.timetuple()) * 1000) +
            (self.article.date.microsecond / 1000)
        )
