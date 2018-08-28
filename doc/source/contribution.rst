Contribution
============
This document describes how to contribute to this project.

Posting Issues
--------------
Posting issue is appreciated. If you found issues, you can report it to
`issues tracker`_. Note that you will need GitHub_ account before you send the
bug report.

When you try to create an issue, you will see the page to choice the type of
the issue you want to create and please choose one of the type. You can also
open regular issue, but describe your issue / question in detail.

.. _`issues tracker`: https://github.com/hiroaki-yamamoto/mongoengine-goodjson/issues
.. _GitHub: https://github.com

Solve your problem by your hand
-------------------------------
This package is distributed as an Open-Source Software under the terms of
`MIT License`_. Hence, you are able to change the code of this package.

.. _`MIT License`: license.html

Testbed Environment
-------------------
As you can see the package, this code is using tox that can test multiple-version
of Python. In particular, this package is using the lates version of Python 3 and
Python 2. To test this package, install packages in requirements.txt like this:

.. code:: bash

  $ pip install -r requirements.txt

If you have `pip-tools`_, you can also install the package by doing this:

.. code:: bash

  $ pip-sync

To keep your system site package clean, using venv is recommended. To use it,
you can make virtual environment before installing the packages:

.. code:: bash

  $ python -m venv venv && source ./venv/bin/activate

Then, run the pip.

To test the code, you can use tox_ or detox_ that is installed by pip:

.. code:: bash

  (venv)$ tox
  # or...
  (venv)$ detox

.. _`pip-tools`: https://github.com/jazzband/pip-tools
.. _tox: https://tox.readthedocs.io/en/latest/
.. _detox: https://pypi.org/project/detox/

Pull Request
------------
If you have coding skills and time to fix your problem, please create a
`Pull Request`_. This is much more appreciated than Posting Issues.

Before sending pull request
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sending pull request is very appreciated, but please note:

- **Test code is mandatory.** Your bug must be re-producible, and writing test code
  is showing the proof of the bug. Pull requests that doesn't have test code might
  be rejected.
- **Not all pull request is merged.** Your pull request is not always accepted
  and/or merged. However, Hiro_ absolutely appreciate your contribution.

Note pull requests that don't follow the above rule might not be merged.

.. _`Pull Request`: https://github.com/hiroaki-yamamoto/mongoengine-goodjson/pulls
.. _Hiro: https://github.com/hiroaki-yamamoto
