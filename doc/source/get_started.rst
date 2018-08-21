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
