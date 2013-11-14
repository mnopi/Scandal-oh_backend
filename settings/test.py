"""Testing settings."""

from .common import *
from settings import common

common.TEST_MODE = True

# Usaremos sqlite3 como BD para testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'test_db',					  # Or path to database file if using sqlite3.
        'USER': '',					  # Not used with sqlite3.
        'PASSWORD': '',				  # Not used with sqlite3.
        'HOST': '',					  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',					  # Set to empty string for default. Not used with sqlite3.
    }
}

INSTALLED_APPS += (
    'selenium',
    'django_nose',
    # 'lettuce.django',
    'tests',
)


# LETTUCE
#########################################
# LETTUCE_APPS = (
#     'tests',
# )
# LETTUCE_AVOID_APPS = (
#     'another_app',
#     'foobar',
# )
# LETTUCE_SERVER_PORT = 7000
#########################################


# NOSE
#########################################
TEST_RUNNER = 'tests.runner.MyTestRunner'
NOSE_ARGS = [
    '-s', # para activar stdout (salida a consola) durante los tests
    '--verbosity=2',
]
#########################################
