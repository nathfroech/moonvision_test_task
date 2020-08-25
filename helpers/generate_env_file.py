#!/usr/bin/env python

"""
Script for .env file generating.

Usage:
`python helpers/generate_env_file.py`

If you need to add a new setting, update `TEMPLATE` constant with line that looks like `SETTING_NAME = setting_value`.
In `TEMPLATE` you may use `{base_dir}` placeholder to substitute base project path. If you want to add more
substitutions - update the returning dict of the function `create_context`.
"""

import argparse
import hashlib
import pathlib
import random
import string
import sys
import time
from typing import Any, Dict

try:  # noqa: WPS229
    # Inspired by
    # https://github.com/django/django/blob/master/django/utils/crypto.py
    random = random.SystemRandom()  # type: ignore
    using_sysrandom = True
except NotImplementedError:
    using_sysrandom = False

# TODO: Add your settings into these templates like `SETTING_NAME = setting_value`
# Note: If you are using Docker, you will need to change "localhost" to correct hosts in Redis and PostgreSQL variables
REDIS_SETTINGS_TEMPLATE = """
# Redis
# ------------------------------------------------------------------------------
REDIS_URL=redis://localhost:6379/0
""".strip()

LOCAL_TEMPLATE = """
# General
# ------------------------------------------------------------------------------
PROJECT_ROOT = {base_dir}
PROJECT_ENVIRONMENT = debug
DJANGO_SETTINGS_MODULE = config.settings
DJANGO_SECRET_KEY = {secret_key}
DJANGO_ALLOWED_HOSTS = localhost,127.0.0.1

# PostgreSQL
# ------------------------------------------------------------------------------
# DATABASE_URL = postgres://moonvision@localhost:5432/moonvision/
DATABASE_URL = sqlite:///{base_dir}/moonvision.sqlite
""".lstrip()

DEFAULT_ALLOWED_CHARS = string.ascii_letters + string.digits

Context = Dict[str, Any]


def create_arguments_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser('Generate .env file')
    parser.add_argument('--name', dest='file_name', action='store', default='.env')
    parser.add_argument('--rewrite', dest='rewrite', action='store_true')
    return parser


def generate_random_string(length: int = 14, allowed_chars: str = DEFAULT_ALLOWED_CHARS) -> str:
    """
    Generate random string of desired length.

    Example:
        opting out for 50 symbol-long, [a-z][A-Z][0-9] string
        would yield log_2((26+26+10)^50) ~= 334 bit strength.
    """
    if not using_sysrandom:
        # This is ugly, and a hack, but it makes things better than
        # the alternative of predictability. This re-seeds the PRNG
        # using a value that is hard for an attacker to predict, every
        # time a random string is required. This may change the
        # properties of the chosen random sequence slightly, but this
        # is better than absolute predictability.

        # Django uses settings.SECRET_KEY for this, but we cannot use the same strategy, because the code may be
        # executed in environment where Django has not been installed or configured yet
        temporary_secret_key = ''.join(random.choice(DEFAULT_ALLOWED_CHARS) for _ in range(length))
        new_seed = ('{0}{1}{2}'.format(random.getstate(), time.time(), temporary_secret_key)).encode()
        random.seed(hashlib.sha256(new_seed).digest())
    return ''.join(random.choice(allowed_chars) for _ in range(length))


def create_context(base_dir: pathlib.Path) -> Context:
    symbols_to_use = string.ascii_lowercase + string.digits + '!@%^&*(-_=+)'  # noqa: WPS336
    return {
        'base_dir': str(base_dir),
        'secret_key': generate_random_string(50, symbols_to_use),  # noqa: WPS432 Keep the number magic
    }


def render_to_string(template: str, context: Context) -> str:
    return template.format(**context)


def generate_dotenv_file(file_name: str, rewrite: bool = False) -> None:
    project_dir = pathlib.Path(__file__).parents[1].absolute()
    file_path: pathlib.Path = project_dir / file_name
    if file_path.is_file() and not rewrite:
        sys.stdout.write('File {file_name} already exists; skipping file generation.'.format(file_name=file_name))
        return

    file_context = create_context(project_dir)
    generated_file = LOCAL_TEMPLATE.format(**file_context)
    file_path.write_text(generated_file)


if __name__ == '__main__':
    arguments_parser = create_arguments_parser()
    args = arguments_parser.parse_args()
    generate_dotenv_file(args.file_name, args.rewrite)
