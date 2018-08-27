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
