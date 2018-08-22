Getting Started
===============

Why MongoEngine GoodJSON created
--------------------------------
Problem
~~~~~~~
Using MongoEngine to create something (e.g. RESTful API), sometimes you might
want to serialize the data from the db into JSON, but some fields are weird
and not suitable for frontend/api:

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

If you don't mind about :code:`_id`, :code:`$oid`, and :code:`$date`, it's fine.
However, these data might cause problems when you using AngularJS_, because
prefix :code:`$` is reserved by the library.

.. _AngularJS: https://angularjs.org/

In addition to this, object in object might cause
:code:`No such property $oid of undefined` error when you handle the data like
above on the frontend.

The Solution
~~~~~~~~~~~~~
To solve the problems, the generated data should be like this:

.. code:: json

  {
    "id": "5700c32a1cbd5856815051ce",
    "name": "Hiroaki Yamamoto",
    "registered_date": 1459667811724
  }

Making above structure can be possible by doing re-mapping, but if we do it on
API's controller object, the code might get super-dirty:

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


To give the solution of this problem, I developed this scirpt.
By using this script, you will not need to make the transform like above. i.e.

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


Installation
-------------
There's several ways to install MongoEngine GoodJSON. The easiest way is to
install thru pypi_

.. _pypi: https://pypi.org/project/mongoengine_goodjson/

.. code:: bash

  pip install mongoengine_goodjson

As an alternative way, you can download the code from `github release`_,
extract the tgz archive, and execute setup.py:

.. code:: bash

  python setup.py install

.. _`github release`: https://github.com/hiroaki-yamamoto/mongoengine-goodjson/releases

However, if you are able to create `virtual environment`_, you can create one
**before installing this script**.:

.. code:: bash

  python -m venv venv

.. _`virtual environment`: https://docs.python.org/3/tutorial/venv.html
