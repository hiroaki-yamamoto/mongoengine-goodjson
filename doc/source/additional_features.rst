Addtional Features
==================

FollowReferenceField
--------------------
This script also provides a field that supports serialization of the reference
with :code:`follow_reference=True`. Unlike :code:`ReferenceField`, this field
supports deserialization and automatic-save.

To use this field, you can just simply declare the field as usual.
For example, like this:

.. code:: python

  import mongoengine as db
  import mongoengine_goodjson as gj


  class User(gj.Document):
    """User info."""
    name = db.StringField()
    email = db.EmailField()

  class DetailedProfile(gj.Document):
    """Detail profile of the user."""
    # FollowReferenceField without auto-save
    user = gj.FollowReferenceField(User)
    yob = db.DateTimeField()
    # FollowReferenceField with auto-save
    partner = gj.FollowReferenceField(User, autosave=True)
