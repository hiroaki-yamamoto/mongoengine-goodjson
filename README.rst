More human readable JSON serializer/de-serializer for MongoEngine
=================================================================

|Build Status| |Coverage Status| |Code Health| |PyPI version|

What This?
----------

This script has MongoEngine Document json serialization more-natural.

Why this invented?
------------------

Using MongoEngine to create something (e.g. RESTful API), sometimes you
might want to serialize the data from the db into JSON, but some fields
are weird and not suitable for frontend/api:

.. code:: json

    {
      "_id": {
        "$oid": "5700c32a1cbd5856815051ce"
      },
      "name": "Hiroaki Yamamoto",
      "registered_date": {
          "$date": 1459667811724
      }
    }

The points are 2 points:

-  ``_id`` might not be wanted because jslint disagrees ``_`` character
   unless declaring ``jslint nomen:true``
-  There are sub-fields such ``$oid`` and ``$date``. These fields are
   known as `MongoDB Extended
   JSON <https://docs.mongodb.org/manual/reference/mongodb-extended-json/>`__.
   However, considering MongoEngine is ODM and therefore it has
   schema-definition methods, the fields shouldn't have the special
   fields. In particular problems, you might get
   ``No such property $oid of undefined`` error when you handle above
   generated data on frontend.

To solve the problems, the generated data should be like this:

.. code:: json

    {
      "id": "5700c32a1cbd5856815051ce",
      "name": "Hiroaki Yamamoto",
      "registered_date": 1459667811724
    }

Making above structure can be possible by doing re-mapping, but if we do
it on `API's controller
object <https://developer.apple.com/library/ios/documentation/General/Conceptual/DevPedia-CocoaCore/MVC.html>`__,
the code might get super-dirty:

.. code:: python

    """Dirty code."""
    import mongoengine as db


    class User(db.Document):
      """User class."""
      name = db.StringField(required=True, unique=True)
      registered_date = db.DateTimeField()


    def get_user(self):
      """Get user."""
      models = [
        {
          ("id" if key == "_id" else key): (
            value.pop("$oid") if "$oid" in value and isinstance(value, dict)
            else value.pop("$date") if "$date" in value and isinstance(value, dict)
            else value  #What if there are the special fields in child dict?
          )
          for (key, value) in doc.items()
        } for doc in User.objects(pk=ObjectId("5700c32a1cbd5856815051ce"))
      ]
      return json.dumps(models, indent=2)

To give the solution of this problem, I developed this scirpt. By using
this script, you will not need to make the transform like above. i.e.

.. code:: python


    """A little-bit clean code."""

    import mongoengine as db
    import mongoengine_goodjson as gj


    class User(gj.Document):
      """User class."""
      name = db.StringField(required=True, unique=True)
      registered_date = db.DateTimeField()


    def get_user(self):
      """Get user."""
      return model_cls.objects(
        pk=ObjectId("5700c32a1cbd5856815051ce")
      ).to_json(indent=2)

How to use it
-------------

Generally you can define the document as usual, but you might want to
inherits ``mongoengnie_goodjson.Document`` or
``mongoengnie_goodjson.EmbeddedDocument``.

Here is the example:

.. code:: python

    """Example schema."""

    import mongoengine_goodjson as gj
    import mongoengine as db


    class Address(gj.EmbeddedDocument):
        """Address schema."""

        street = db.StringField()
        city = db.StringField()
        state = db.StringField()


    class User(gj.Document):
        """User data schema."""

        name = db.StringField()
        email = db.EmailField()
        address = db.EmbeddedDocumentListField(Address)

Feature: Follow Reference
-------------------------

Adding documents with ``ReferenceField``, the fields are serialized as
ObjectId by default:

``model.py``

.. code:: python

    import mongoengine as db
    import mongoengine_goodjson as gj


    class Book(gj.Document):
      """Book information model."""

      name = db.StringField(required=True)
      isbn = db.StringField(required=True)
      author = db.StringField(required=True)
      publisher = db.StringField(required=True)
      publish_date = db.DateTimeField(required=True)


    class User(gj.Document):
      firstname = db.StringField(required=True)
      lastname = db.StringField(required=True)
      books_bought = db.ListField(db.ReferenceField(Book))
      favorite_one = db.ReferenceField(Book)

``The example of generated output``

.. code:: json

    {
      "id": "570ee9d1fec55e755db82129",
      "firstname": "James",
      "lastname": "Smith",
      "books_bought": [
        "570eea0afec55e755db8212a",
        "570eea0bfec55e755db8212b",
        "570eea0bfec55e755db8212c"
      ],
      "favorite_one": "570eea0bfec55e755db8212b"
    }

This seems to be good deal for ``Reference Field``, but sometimes you
might want to generate the Document with Referenced Document like
Embedded Document:

.. code:: json

    {
      "id": "570ee9d1fec55e755db82129",
      "firstname": "James",
      "lastname": "Smith",
      "books_bought": [
        {
          "id": "570eea0afec55e755db8212a",
          "name": "ドグラ・マグラ (上)",
          "author": "夢野 久作",
          "publisher": "角川文庫",
          "publish_date": "1976-10-01",
          "isbn": "978-4041366035"
        },
        {
          "id": "570eea0bfec55e755db8212b",
          "name": "ドグラ・マグラ (下)",
          "author": "夢野 久作",
          "publisher": "角川文庫",
          "publish_date": "1976-10-01",
          "isbn": "978-4041366042"
        },
        {
          "id": "570eea0bfec55e755db8212c",
          "name": "The Voynich Manuscript: Full Color Photographic Edition",
          "author": "Unknown",
          "publisher": "FQ Publishing",
          "publish_date": "2015-01-17",
          "isbn": "978-1599865553"
        }
      ],
      "favorite_one": {
        "id": "570eea0bfec55e755db8212b",
        "name": "ドグラ・マグラ (下)",
        "author": "夢野 久作",
        "publisher": "角川文庫",
        "publish_date": "1976-10-01",
        "isbn": "978-4041366042"
      }
    }

Making this format can be done by making Document.objects query for each
reference. However, doing it, the code would be also dirty:

.. code:: python

    def output_references():
      user = User.objects(pk=ObjectId("570ee9d1fec55e755db82129")).get()
      user_dct = json.loads(user.to_json())
      user_dct["books"] = [
        json.loads(book.to_json()) for book in user.books_bought
      ]
      user_dct["favorite_one"] = json.loads(user.favorite_one.to_json())
      return jsonify(user_dct)
      # ...And what if there are references in the referenced document??

To avoid this annoying problem, this script has new function called
``Follow Reference`` since 0.9. To use it, you can just set
``follow_reference=True`` on serialization:

.. code:: python

    def output_references():
      user = User.objects(pk=ObjectId("570ee9d1fec55e755db82129")).get()
      return jsonify(json.loads(user.to_json(follow_reference=True)))

Note that setting ``follow_reference=True``, ``Document.to_json`` checks
the reference recursively until the depth is reached 3rd depth. To
change the maximum recursion depth, you can set the value you want to
``max_depth``:

.. code:: python

    def output_references():
      user = User.objects(pk=ObjectId("570ee9d1fec55e755db82129")).get()
      return jsonify(json.loads(user.to_json(follow_reference=True, max_depth=5)))

Feature: FollowReferenceField
-----------------------------

This script also provides a field that supports serialization of the
reference with ``follow_reference=True``. Unlike ``ReferenceField``,
this field supports deserialization and automatic-save.

To use this field, you can just simply declare the field as usual. For
example, like this:

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

Important Note when use FollowReferenceField
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Currently, FollowReferenceField doesn't support the limit of recursion.
Therefore, **don't implement self-reference document and/or
loop-reference document.**

Feature 2: Exclude fields from JSON serialization/deserialization
-----------------------------------------------------------------

Sometimes you might want to exclude fields from JSON serialization, but
to do so, you might need to decode JSON-serialized string, pop the key,
then, serialize the dict object again. Since 0.11, metadata
``exclude_to_json``, ``exclude_from_json``, and ``exclude_json`` are
available and they behave like the following:

-  Setting Truthy value to ``exclude_to_json``, the corresponding field
   is omitted from JSON encoding. Note that this excludes fields JSON
   encoding only.
-  Setting Truthy value to ``exclude_from_json``, the corresponding
   field is omitted from JSON decoding. Note that this excludes fields
   JSON decoding only.
-  Setting Truhy value to ``exclude_json``, the corresponding field is
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

Not implemented list
--------------------

The following types are partially implemented because there aren't any
corresponding fields on MongoEngine:

+-------------+------------------------+-----------+
| Type        | Encoder                | Decoder   |
+=============+========================+===========+
| Regex       | :white\_check\_mark:   | :x:       |
+-------------+------------------------+-----------+
| MinKey      | :white\_check\_mark:   | :x:       |
+-------------+------------------------+-----------+
| MaxKey      | :white\_check\_mark:   | :x:       |
+-------------+------------------------+-----------+
| TimeStamp   | :white\_check\_mark:   | :x:       |
+-------------+------------------------+-----------+
| Code        | :white\_check\_mark:   | :x:       |
+-------------+------------------------+-----------+

The following document types are not implemented yet:

-  ``DynamicDocument``
-  ``DynamicEmbeddedDocument``
-  ``MapReduceDocument``

Btw I don't think above documents implementations are needed because
they can be handled by using multiple-inheritance. If you couldn't do
it, post issue or PR.

FollowReference Decoder
~~~~~~~~~~~~~~~~~~~~~~~

[STRIKEOUT:Since 0.9, this script supports Follow Reference, but it
doesn't support decoder. Passing "followed reference" dict to
ReferenceField, it recognized ``id`` field only. This behavior will be
fixed at 0.10.] Use ``FollowReferenceField``.

Contribute
----------

This scirpt is coded on TDD. i.e. Writing a test that fails, and then
write the actual code to pass the test. Therefore, ``virtualenv``,
``nose`` and ``tox`` will be needed to code this script. In addtion, you
will need to have `MongoDB <https://www.mongodb.org/>`__ installed and
it must be running on the computer to run the tests.

In addition, you can use `gulp <http://gulpjs.com/>`__ to watch the file
changes.

License (MIT License)
---------------------

Copyright (c) 2016 Hiroaki Yamamoto

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

.. |Build Status| image:: https://travis-ci.org/hiroaki-yamamoto/mongoengine-goodjson.svg?branch=master
   :target: https://travis-ci.org/hiroaki-yamamoto/mongoengine-goodjson
.. |Coverage Status| image:: https://coveralls.io/repos/github/hiroaki-yamamoto/mongoengine-goodjson/badge.svg?branch=master
   :target: https://coveralls.io/github/hiroaki-yamamoto/mongoengine-goodjson?branch=master
.. |Code Health| image:: https://landscape.io/github/hiroaki-yamamoto/mongoengine-goodjson/master/landscape.svg?style=flat
   :target: https://landscape.io/github/hiroaki-yamamoto/mongoengine-goodjson/master
.. |PyPI version| image:: https://badge.fury.io/py/mongoengine_goodjson.svg
   :target: https://badge.fury.io/py/mongoengine_goodjson
