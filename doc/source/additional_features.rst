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


Exclude fields from JSON serialization/deserialization
------------------------------------------------------
Sometimes you might want to exclude fields from JSON serialization, but to do
so, you might need to decode JSON-serialized string, pop the key, then, serialize
the dict object again. Since 0.11, metadata :code:`exclude_to_json`,
:code:`exclude_from_json`, and code:`exclude_json` are available and they
exclude field on the following specific actions:

- Setting Truthy value to :code:`exclude_to_json`, the corresponding field is
  omitted from JSON encoding. Note that this excludes fields JSON encoding only.
- Setting Truthy value to :code:`exclude_from_json`, the corresponding field is
  omitted from JSON decoding. Note that this excludes fields JSON decoding only.
- Setting Truhy value to :code:`exclude_json`, the corresponding field is
  omitted from JSON encoding and decoding.

Example
~~~~~~~
To use the exclusion, you can just put exclude metadata like this:

.. code:: python

  import mongoengine_goodjson as gj
  import mongoengine as db


  class ExclusionModel(gj.Document):
      """Example Model."""
      to_json_exclude = db.StringField(exclude_to_json=True)
      from_json_exclude = db.IntField(exclude_from_json=True)
      json_exclude = db.StringField(exclude_json=True)
      required = db.StringField(required=True)


  def get_json_obj(*q, **query):
      model = Exclude.objects(*q, **query).get()
      # Just simply call to_json :)
      return model.to_json()


  def get_json_list(*q, **query):
      # You can also get JSON serialized text from QuerySet.
      return Exclude.objects(*q, **query).to_json()


  # Decoding is also simple.
  def get_obj_from_json(json_text):
    return Exclude.from_json(json_text)


  def get_list_from_json(json_text):
    return Exclude.objects.from_json(json_text)


Reference Limit
---------------
Since version 1.0.0, the method to limit recursive depth is implemented.

By default, :code:`to_json` serializes the document until the cursor reaches
3rd level. To change the maximum depth level, change :code:`max_depth` kwargs.

As of 1.1.0, callable function can be set to :code:`max_depth`, and
:code:`to_json` calls max_depth with the document that the field holds, and
current depth level. If the function that is associated with :code:`max_depth`
returns truthy values, the serialization will be stop.

Note that when you use callable :code:`max_depth` of
:code:`FollowReferenceField`, the border of the document i.e. the document
that :code:`max_depth` returned truthy value, will **NOT** be serialized while
:code:`to_json()` does. It just be "id" of the model.

Code Example
~~~~~~~~~~~~
Here is the code example of Limit Recursion:

.. code:: python

  import mongoengine as db
  import mongoengine_goodjson as gj


  class User(gj.Document):
    """User info."""
    name = db.StringField()
    email = db.EmailField()
    # i.e. You can access everyone in the world by Six Degrees of Separation
    friends = db.ListField(gj.FollowReferenceField("self", max_depth=6))

    # If the name of the user is Alice, Mary, or Bob, it will refer more depth.
    not_friend = gj.FollowReferenceField(
      "self", max_depth=lambda doc, cur_depth: doc.name not in [
        "Alice", "Mary", "Bob"
      ]
    )

  class DetailedProfile(gj.Document):
    """Detail profile of the user."""
    user = gj.FollowReferenceField(User)
    yob = db.DateTimeField()


To disable the limit, put negative number to :code:`max_depth`, however you
should make sure that the model has neither circuit nor self-reference.
