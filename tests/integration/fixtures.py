#!/usr/bin/env python
# coding=utf-8

"""Fixtures for integration tests."""

from base64 import b64encode
from datetime import datetime, timedelta
from calendar import timegm
from uuid import uuid5, NAMESPACE_DNS

from bson import ObjectId, Binary
from bson.py3compat import text_type

from .schema import (
    User, Address, Article, Email, ArticleMetaData, Seller, Reference,
    ExtraReference, ExtraInformation
)

now = datetime.utcnow()

user = User(
    id=ObjectId(), name="Test man", email="test@example.com",
    address=[
        Address(
            street=("Test street %d" % counter),
            city=("Test city %d" % counter),
            state=("Test state %d" % counter)
        ) for counter in range(3)
    ]
)
users = [
    User(
        id=ObjectId(),
        name="Test man %d" % c1, email="test%d@example.com" % c1,
        address=[
            Address(
                street=("Test street %d %d" % (c1, c2)),
                city=("Test city %d %d" % (c1, c2)),
                state=("Test state %d %d" % (c1, c2))
            ) for c2 in range(3)
        ]
    ) for c1 in range(3)
]

user_dict = {
    u"id": text_type(user.pk),
    u"name": text_type(user.name),
    u"email": text_type(user.email),
    u"address": [
        {
            u"street": text_type(address.street),
            u"city": text_type(address.city),
            u"state": text_type(address.state)
        } for address in user.address
    ]
}

users_dict = [
    {
        u"id": text_type(user_el.pk),
        u"name": text_type(user_el.name),
        u"email": text_type(user_el.email),
        u"address": [
            {
                u"street": text_type(address.street),
                u"city": text_type(address.city),
                u"state": text_type(address.state)
            } for address in user_el.address
        ]
    } for user_el in users
]

email = Email(email="test@example.com")
email_dict_id = {"id": email.pk}
email_dict_email = {"id": email.pk}

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

reference_extra_info = ExtraInformation(txt="This is a test")
reference_extra_ref = ExtraReference(pk=ObjectId(), ref_txt="Reference test")

reference = Reference(
    pk=ObjectId(), name="test", references=[article],
    ex_info=reference_extra_info, ex_ref=reference_extra_ref
)
reference_dict = {
    u"id": text_type(reference.id),
    u"name": u"test",
    u"references": [article_dict.copy()],
    u"ex_info": {
        u"txt": reference_extra_info.txt
    },
    u"ex_ref": {
        u"_id": {u"$oid": str(reference_extra_ref.id)},
        u"ref_txt": reference_extra_ref.ref_txt
    }
}
reference_dict["references"][0]["user"] = user_dict.copy()
