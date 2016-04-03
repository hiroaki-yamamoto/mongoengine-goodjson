#!/usr/bin/env python
# coding=utf-8

"""Fixtures for integration tests."""

from base64 import b64encode
from calendar import timegm
from datetime import datetime, timedelta
from uuid import uuid5, NAMESPACE_DNS

from bson import ObjectId, Binary

from .schema import User, Address, Article, Email, ArticleMetaData, Seller

now = datetime.utcnow()

user = User(
    name="Test man", email="test@example.com",
    address=[
        Address(
            street=("Test street %d" % counter),
            city=("Test city %d" % counter),
            state=("Test state %d" % counter)
        ) for counter in range(3)
    ]
)
user.pk = ObjectId()
user_dict = {
    u"id": str(user.pk),
    u"name": user.name,
    u"email": user.email,
    u"address": [
        {
            u"street": "Test street %d" % counter,
            u"city": "Test city %d" % counter,
            u"state": "Test state %d" % counter
        } for counter in range(3)
    ]
}

email = Email(email="test@example.com")
email_dict_id = {"id": email.pk}
email_dict_email = {"id": email.pk}

article = Article(
    user=user, title="Test Tile",
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
article.pk = ObjectId()
article_dict = {
    u"id": str(article.pk),
    u"user": user_dict["id"],
    u"title": article.title,
    u"date": int(
        timegm(article.date.timetuple())*1000 +
        article.date.microsecond / 1000
    ),
    u"body": {
        u"data": str(b64encode(article.body).decode("utf-8")),
        u"type": article.body.subtype
    },
    u"uuid": str(article.uuid),
    u"addition": {
        u"price": article.addition.price,
        u"seller": {
            u"name": article.addition.seller.name,
            u"address": {
                u"street": article.addition.seller.address.street,
                u"city": article.addition.seller.address.city,
                u"state": article.addition.seller.address.state
            }
        }
    }
}
