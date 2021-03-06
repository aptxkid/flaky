flaky
=====

.. image:: https://travis-ci.org/box/flaky.png?branch=master
    :target: https://travis-ci.org/box/flaky

.. image:: https://pypip.in/v/flaky/badge.png
    :target: https://pypi.python.org/pypi/flaky

.. image:: https://pypip.in/d/flaky/badge.png
    :target: https://pypi.python.org/pypi/flaky

Flaky is a plugin for nose that automatically reruns flaky tests.

Ideally, tests reliably pass or fail, but sometimes test fixtures must rely on components that aren't 100%
reliable. With flaky, instead of removing those tests or marking them to @skip, they can be automatically
retried.

Like any nose plugin, flaky can be activated via the command line:

.. code-block:: console

    nosetests --with-flaky

To mark a test as flaky, simply decorate it with @flaky():

.. code-block:: python

    @flaky
    def test_something_that_usually_passes(self):
        value_to_double = 21
        result = get_result_from_flaky_doubler(value_to_double)
        self.assertEqual(result, value_to_double * 2, 'Result doubled incorrectly.')

By default, flaky will retry a failing test once, but that behavior can be overridden by passing values to the
flaky decorator. It accepts two parameters: max_runs, and min_passes; flaky will run tests up to max_runs times, until
it has succeeded min_passes times. Once a test passes min_passes times, it's considered a success; once it has been
run max_runs times without passing min_passes times, it's considered a failure.

.. code-block:: python

    @flaky(max_runs=3, min_passes=2)
    def test_something_that_usually_passes(self):
        """This test must pass twice, and it can be run up to three times."""
        value_to_double = 21
        result = get_result_from_flaky_doubler(value_to_double)
        self.assertEqual(result, value_to_double * 2, 'Result doubled incorrectly.')

In addition to marking a single test flaky, entire test cases can be marked flaky:

.. code-block:: python

    @flaky
    class TestMultipliers(TestCase):
        def test_flaky_doubler(self):
            value_to_double = 21
            result = get_result_from_flaky_doubler(value_to_double)
            self.assertEqual(result, value_to_double * 2, 'Result doubled incorrectly.')

        @flaky(max_runs=3)
        def test_flaky_tripler(self):
            value_to_triple = 14
            result = get_result_from_flaky_tripler(value_to_triple)
            self.assertEqual(result, value_to_triple * 3, 'Result tripled incorrectly.')

The @flaky() class decorator will mark test_flaky_doubler as flaky, but it won't override the 3 max_runs
for test_flaky_tripler (from the decorator on that test method).

Additional usage examples are in the code - see test/test_example.py

Installation
------------

To install, simply:

.. code-block:: console

    pip install flaky


Contributing
------------

See `CONTRIBUTING <https://github.com/box/flaky/blob/master/CONTRIBUTING.rst>`_.


Setup
~~~~~

Create a virtual environment and install packages -

.. code-block:: console

    mkvirtualenv flaky
    pip install -r requirements-dev.txt


Testing
~~~~~~~

Run all tests using -

.. code-block:: console

    tox

The tox tests include code style checks via pep8 and pylint.


Copyright and License
---------------------

::

 Copyright 2014 Box, Inc. All rights reserved.

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
