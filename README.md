# More human readable JSON serializer/de-serializer for MongoEngine
[![Build Status]][Status Link]
[![Coverage Status]][Coverage Link]
[![Code Health]][Health Link]

[Build Status]: https://travis-ci.org/hiroaki-yamamoto/mongoengine-goodjson.svg?branch=master
[Status Link]: https://travis-ci.org/hiroaki-yamamoto/mongoengine-goodjson
[Coverage Status]: https://coveralls.io/repos/github/hiroaki-yamamoto/mongoengine-goodjson/badge.svg?branch=master
[Coverage Link]: https://coveralls.io/github/hiroaki-yamamoto/mongoengine-goodjson?branch=master
[Code Health]: https://landscape.io/github/hiroaki-yamamoto/mongoengine-goodjson/master/landscape.svg?style=flat
[Health Link]: https://landscape.io/github/hiroaki-yamamoto/mongoengine-goodjson/master

## What This?
This script havs MongoEngine Document json serialization more-natural.

## Why you invent?

When you use [MongoEngine] and create RESTful API, sometimes you might want to
serialize the data from the db into JSON. However, the generated JSON
is weired at some fields:

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

* `_id` might be not wanted because jslint disagrees `_` character unless
  declaring `jsling nomen:true`
* There are sub-fields such `$oid` and `$date`. These fields are known as
  [MongoDB Extended JSON]. However, considering MongoEngine is ODM and
  therefore it has schema-definition methods, the fields shouldn't have the
  special fields. In particular problems, you might get
  `No such property $oid on undefined` error when you handle above generated
  data on frontend.

To solve the problems, the generated data should be like this:

```JSON
{
  "id": "5700c32a1cbd5856815051ce",
  "name": "Hiroaki Yamamoto",
  "registered_date": 1459667811724
}
```

Making above structure possible by doing re-mapping, but if we do it on
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

Generally You can define the document as usual, but you might want to inherits
`mongoengnie_goodjson.Document` or `mongoengnie_goodjson.EmbeddedDocument`.

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

## Not implemented list
The following types are partially implemented because there aren't any
corresponding fields on MongoEngine:

Type|Encoder|Decoder
----|--------|-------
Regex|:white_check_mark:|:x:
MinKey|:white_check_mark:|:x:
MaxKey|:white_check_mark:|:x:
TimeStamp|:white_check_mark:|:x:
Code|:white_check_mark:|:x:

The following document types are not implemented yet:

* `DynamicDocument`
* `DynamicEmbeddedDocument`
* `MapReduceDocument`

Btw I don't think above documents implementations are needed because they can
be handled by using multiple-inheritance. If you couldn't do it, post issue or PR.

## License (MIT License)
Copyright (c) 2016 Hiroaki Yamamoto

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
