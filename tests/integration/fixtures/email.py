#!/usr/bin/env python
# coding=utf-8

"""Email."""

from six import text_type

from ..schema import Email


email = Email(email="test@example.com")
email_dict_id = {text_type("id"): email.pk}
email_dict_email = {text_type("id"): email.pk}
