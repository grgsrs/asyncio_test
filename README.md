# asyncio_test

This repository contains source code for a presentation I gave
at [PyCon AU 2017](https://2017.pycon-au.org/) called "A
Really Gentle Introduction to Asyncio." A video of the
presentation is available at: http://youtu.be/3mb9jFAHRfw

## Requirements

The demo was developed with:

* [Python 3.6](http://www.python.org)
* [pytest 3.2.0](https://doc.pytest.org/)
* [pytest-asyncio 0.6.0](https://pypi.python.org/pypi/pytest-asyncio)
* [Protobuf 3.3.0](https://pypi.python.org/pypi/protobuf)

To run the tests

    cd asyncio_test/tests
    PYTHONPATH=.. py.test

## Changes

I neglected to properly clean up the ATM subprocess in the
original code, causing the demo to fail intermittently and,
embarassingly, during my presentation. I've fixed this now.
