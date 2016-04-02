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

## Important Note
This is under heavy development and it is not recommend to use this lib yet.

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
