Dive in the deep
================

Encoder / Decoder
-----------------
Unlike `JSON encoder / decoder at pytmongo`_, :code:`mongoengine_goodjson` passes
encoder / decoder to `json.dump`_ and `json.load`_ by using :code:`cls` and
:code:`object_hook`. Therefore, passing :code:`args` or :code:`kwargs` to
:code:`mongoengine_goodjson.Document.to_json` /
:code:`mongoengine_goodjson.Document.from_json`, The arguments are put into
`json.dump`_ and `json.load`_.


.. _`JSON encoder / decoder at pytmongo`:
  https://github.com/mongodb/mongo-python-driver/blob/master/bson/json_util.py

.. _`json.dump`: https://docs.python.org/dev/library/json.html#json.dump

.. _`json.load`: https://docs.python.org/dev/library/json.html#json.load

Code Example
~~~~~~~~~~~~
Here's the example code what this section is saying. In this code, the document
tries to serialize date into epoch time format (not ISO format).

.. code:: python

  import mongoengine as db
  import mongoengine_goodjson as gj


  class User(gj.Document):
    """User class."""
    name = db.StringField(required=True, unique=True)
    registered_date = db.DateTimeField()

    def to_json(self, *args, **kwargs):
      """Serialize into json."""
      return super(User, self).to_json(epoch_mode=True)

FAQ from issue tracker
----------------------

Q: I'm using third-party package such as `flask-mongoengine`_, but no ObjectId
is replaced (`#34`_)

A: Some third-party package has abstract classes that inherit classes from
MongoEngine. To use :code:`mongoengine_goodjson` with those packages, you will
need to inherit the both of documents and queryset.

Example Code
~~~~~~~~~~~~
Here is the example code to solve inheritance problem.

.. code:: python

  import mongoengine as db
  import flask_mongoengine as fm
  import mongoengine_goodjson as gj

  class QuerySet(fm.BaseQuerySet, gj.QuerySet):
    """Queryset."""
    pass


  class Document(db.Document, gj.Document):
    """Document."""
    meta = {
      'abstract': True,
      'queryset_class': QuerySet
    }


  class User(Document):
    """User class."""
    name = db.StringField(required=True, unique=True)
    registered_date = db.DateTimeField()

.. _`flask-mongoengine`: https://github.com/MongoEngine/flask-mongoengine
.. _`#34`: https://github.com/hiroaki-yamamoto/mongoengine-goodjson/issues/34

Q: Is there a way to specify which format a DatetimeField will be resolved to? (`#38`_)

A: Check `Encoder / Decoder`_

.. _`#38`: https://github.com/hiroaki-yamamoto/mongoengine-goodjson/issues/38
