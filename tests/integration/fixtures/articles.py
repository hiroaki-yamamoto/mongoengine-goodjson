#!/usr/bin/env python
# coding=utf-8

"""Article fixtures."""

from base64 import b64encode
from calendar import timegm
from datetime import datetime, timedelta
from uuid import uuid5, NAMESPACE_DNS

from bson import ObjectId, Binary
from six import text_type

from .user import user, user_dict
from ..schema import Article, ArticleMetaData, Seller, Address

now = datetime.utcnow()

article = Article(
    pk=ObjectId(), user=user, title="Test Tile",
    date=now - timedelta(microseconds=now.microsecond % 1000),
    body=Binary(b"\x00\x01\x02\x03\x04"),
    uuid=uuid5(NAMESPACE_DNS, "This is a test"),
    addition=ArticleMetaData(
        seller=Seller(
            name="Musle Woman",
            address=Address(
                street="Test musle street",
                city="Test musle city",
                state="Test musle state"
            )
        ),
        price=1000000
    )
)
article_dict = {
    u"id": text_type(article.pk),
    u"user": text_type(user_dict["id"]),
    u"title": text_type(article.title),
    u"date": text_type(article.date.isoformat()),
    u"body": {
        u"data": text_type(b64encode(article.body).decode("utf-8")),
        u"type": article.body.subtype
    },
    u"uuid": text_type(article.uuid),
    u"addition": {
        u"price": article.addition.price,
        u"seller": {
            u"name": text_type(article.addition.seller.name),
            u"address": {
                u"street": text_type(article.addition.seller.address.street),
                u"city": text_type(article.addition.seller.address.city),
                u"state": text_type(article.addition.seller.address.state)
            }
        }
    }
}
article_ref_fld_dict = article_dict.copy()
article_ref_fld_dict["user"] = user_dict.copy()

article_dict_epoch = article_dict.copy()
article_dict_epoch["date"] = int(
    (timegm(article.date.timetuple()) * 1000) +
    (article.date.microsecond / 1000)
)
