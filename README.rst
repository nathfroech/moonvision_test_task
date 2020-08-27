MoonVision REST endpoint test task
==================================

MoonVision REST endpoint test task

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django
.. image:: https://img.shields.io/badge/style-wemake-000000.svg
    :target: https://github.com/wemake-services/wemake-python-styleguide
    :alt: wemake.services code style

:License: MIT

This project implements the REST endpoint for image classification. Enpoint is available on ``/upload-image/`` url and
accepts POST requests with the following JSON data:

.. code-block:: json

    {
        "model_type": "<any value from AlexNet, ResNet, DenseNet, GoogleNet, Inception3, MobileNetV2",
        "image": "<base64-encoded image, either as a plain text or as a data uri>"
    }

There is a docker-compose file to run the project; just run::

    $ docker-compose build
    $ docker-compose up -d

Alternatively, check the `Initial Setup`_ section for running the project locally.

**Answers to the questions from the task.**

    Did you see any difficulty in this API design? What would you change?

The answer actually depends on how and by whom this endpoint will be used, but I'd consider two changes for this API:

* If the endpoint is planned to be used by people who generally do not familiar
  with image classification, it may be hard for them to choose the right model_type.
  In this case it would probably be better to make this field optional or hide
  it entirely and make this decision on server side instead.
* It may be inconvenient that you will have to encode image before sending it.
  There might be several approaches to simplify it:

  * Let user to upload image directly as a part of multipart request.
  * Accept an image url.
  * Implement another endpoint which would accept either file or url and return
    an encoded image.

..

  Explain in 4 sentences what you would do next to scale out this solution

Of course, first of all we will need to decide if we need scaling at all and what do
we need to scale - but there are two obvious parts in our API which may require scaling:
django app itself and the image classification.

For django app scaling there are some common techniques that could be used, like
increasing HTTP server workers or using cache.

As for the image classification - one of the obvious choices would be to make
it work on GPU instead of CPU. Also it might make sense to make the classification
process asynchronous, either by reimplementing this endpoint on some async framework
or by using a queue and making an actual classification in some async task.

Initial Setup
-------------

I would prefer to have a virtualenv on host machine even if we will use docker.
Moreover, we need to configure git hooks and generate .env file.

To make an initial setup, run these commands at project root::

    $ virtualenv -p python3.8 env
    $ source env/bin/activate
    $ make init_project
    $ ./manage.py migrate
    $ ./manage.py createsuperuser

Settings
--------

All environment-dependent or confidential settings should be declared as environment variables. As an alternative, you
may create ``.env`` file at project root, which would contain all such variables.

Command ``make env_file`` will create such file with defaults, that should be replaced with actual values.

Basic Commands
--------------

Updating requirements
`````````````````````

Project uses `pip-tools
<https://github.com/jazzband/pip-tools>`_ for requirements management. If you need to add a new requirement, go to
``requirements`` directory and change the corresponding \*.in file. After that call ``make requirements`` to
compile \*.txt files and synchronize local environment.

For requirements installation in CI or production environments it is enough to simply call ``pip install -r
requirements/<file_name>.txt``.

Setting Up Your Users
`````````````````````

* To create an **superuser account**, use this command::

    $ python manage.py createsuperuser


* There is no support for regular user accounts (unless you add them manually
  to database via console or Django admin panel).

Linting
```````

EditorConfig
''''''''''''
There is ``.editorconfig`` file at the project root, which describes some basic rules for IDE. PyCharm supports it out
of the box, for other IDEs you may have to install a plugin.

Visit https://editorconfig.org/ for additional information.

Commit hooks
''''''''''''
You may run linters after every commit so that they prevent committing code that has some problems. To do this, execute
``pre-commit install``.

This will install all hooks, described at configuration file ``.pre-commit-config.yaml``.

If you wish to run all checks manually, execute ``pre-commit run --all-files`` (or ``make lint``).
For running only a single specific check use ``pre-commit run <hook_id> --all-files`` (you can find hook id of the
desired check at ``.pre-commit-config.yaml``).

Note that ``pre-commit`` checks only files that are tracked by ``git``.

You can find tool documentation at https://pre-commit.com/.

Type checks
```````````

Running type checks with mypy:

::

  $ mypy . --show-error-codes

Tests
`````

Project uses ``pytest`` for testing.

All tests should be placed inside ``tests/`` directory of the corresponding project and (ideally) follow the project
structure - for example, tests for models from app ``user`` should be located at ``user/tests/test_models.py`` (or
inside the package ``user/tests/models/``, if there are too many tests).

As an alternative, tests may be placed inside ``tests/`` directory at the project's root (for example, if tests are not
related to any certain app).

For assertions either default python's ``assert`` can be used, or more specific assertions from PyHamcrest_ - may be
useful for complex assertions and just more readable.

.. _PyHamcrest: https://pyhamcrest.readthedocs.io/en/release-1.8/library/

To run tests: ``make test``.
To run tests and receive a coverage statistics: ``make coverage``.
