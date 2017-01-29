#!/usr/bin/env python
# coding=utf-8

"""User fixture."""

from six import text_type
from bson import ObjectId
from ..schema import User, Address


user = User(
    id=ObjectId(), name="Test man", email="test@example.com",
    address=[
        Address(
            street=(("Test street {}").format(counter)),
            city=(("Test city {}").format(counter)),
            state=(("Test state {}").format(counter))
        ) for counter in range(3)
    ]
)

users = [
    User(
        id=ObjectId(),
        name=("Test man {}").format(c1),
        email=("test{}@example.com").format(c1),
        address=[
            Address(
                street=(("Test street {} {}").format(c1, c2)),
                city=(("Test city %d %d").format(c1, c2)),
                state=(("Test state %d %d").format((c1, c2)))
            ) for c2 in range(3)
        ]
    ) for c1 in range(3)
]

user_dict = {
    text_type("id"): text_type(user.pk),
    text_type("name"): text_type(user.name),
    text_type("email"): text_type(user.email),
    text_type("address"): [
        {
            text_type("street"): text_type(address.street),
            text_type("city"): text_type(address.city),
            text_type("state"): text_type(address.state)
        } for address in user.address
    ]
}

users_dict = [
    {
        text_type("id"): text_type(user_el.pk),
        text_type("name"): text_type(user_el.name),
        text_type("email"): text_type(user_el.email),
        text_type("address"): [
            {
                text_type("street"): text_type(address.street),
                text_type("city"): text_type(address.city),
                text_type("state"): text_type(address.state)
            } for address in user_el.address
        ]
    } for user_el in users
]
