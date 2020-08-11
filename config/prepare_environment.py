import os
import pathlib
import sys

from dotenv import load_dotenv


def prepare_environment() -> None:
    load_dotenv()

    # We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks if running multiple sites in the
    # same mod_wsgi process. To fix this, use mod_wsgi daemon mode with each site in its own daemon process, or use
    # os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    # This allows easy placement of apps within the interior moonvision directory.
    current_path = pathlib.Path(__file__).parent
    sys.path.append(str(current_path.joinpath('moonvision')))
