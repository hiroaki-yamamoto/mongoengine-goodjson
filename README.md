# More human readable JSON serializer/de-serializer for MongoEngine
[![Build Status]][Status Link]
[![Test Coverage]][Test Coverage Link]
[![Maintainability]][Maintainability Link]
[![Documentation Status Image]][DocLink]

[Build Status]: https://circleci.com/gh/hiroaki-yamamoto/mongoengine-goodjson.svg?style=svg
[Status Link]: https://circleci.com/gh/hiroaki-yamamoto/mongoengine-goodjson
[Test Coverage]: https://api.codeclimate.com/v1/badges/7efc2a1bb3040cda0d4f/test_coverage
[Test Coverage Link]: https://codeclimate.com/github/hiroaki-yamamoto/mongoengine-goodjson/test_coverage
[Maintainability]: https://api.codeclimate.com/v1/badges/7efc2a1bb3040cda0d4f/maintainability
[Maintainability Link]: https://codeclimate.com/github/hiroaki-yamamoto/mongoengine-goodjson/maintainability
[Documentation Status Image]: https://readthedocs.org/projects/mongoengine-goodjson/badge/?version=latest
[DocLink]: https://mongoengine-goodjson.readthedocs.io/en/latest/?badge=latest

## What This?
This script has MongoEngine Document json serialization more-natural.

## Why this invented?

Using MongoEngine to create something (e.g. RESTful API), sometimes you
might want to serialize the data from the db into JSON, but some fields
are weird and not suitable for frontend/api:

```JSON
{
  "_id": {
    "$oid": "5700c32a1cbd5856815051ce"
  },
  "name": "Hiroaki Yamamoto",
  "registered_date": {
      "$date": 1459667811724
  }
}
```

The points are 2 points:

* `_id` might not be wanted because jslint disagrees `_` character unless
  declaring `jslint nomen:true`
* There are sub-fields such `$oid` and `$date`. These fields are known as
  [MongoDB Extended JSON]. However, considering MongoEngine is ODM and
  therefore it has schema-definition methods, the fields shouldn't have the
  special fields. In particular problems, you might get
  `No such property $oid of undefined` error when you handle above generated
  data on frontend.

To solve the problems, the generated data should be like this:

```JSON
{
  "id": "5700c32a1cbd5856815051ce",
  "name": "Hiroaki Yamamoto",
  "registered_date": 1459667811724
}
```

Making above structure can be possible by doing re-mapping, but if we do it on
[API's controller object], the code might get super-dirty:

```Python
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
```

To give the solution of this problem, I developed this scirpt. By using this
script, you will not need to make the transform like above. i.e.

```Python

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
```


[MongoEngine]: http://mongoengine.org/
[MongoDB Extended JSON]: https://docs.mongodb.org/manual/reference/mongodb-extended-json/
[API's controller object]: https://developer.apple.com/library/ios/documentation/General/Conceptual/DevPedia-CocoaCore/MVC.html

## How to use it

Generally you can define the document as usual, but you might want to inherits
`mongoengine_goodjson.Document` or `mongoengine_goodjson.EmbeddedDocument`.

Here is the example:

```Python
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
```

## More details... there's the doc!
If you want to know more, there's [read the doc] that you want to read.
You can now [read the doc] with drinking a cup of coffee!!

## Contribute
Please [read the doc] for the detail.

[read the doc]: https://mongoengine-goodjson.readthedocs.io/

## License (MIT License)
See [LICENSE.md](LICENSE.md)
