# terrain.py
import os
import shutil
from lettuce import before, after, world
from splinter.browser import Browser
from django.test.utils import setup_test_environment, teardown_test_environment
from django.core.management import call_command
from django.db import connection
from django.conf import settings
from settings.common import MEDIA_ROOT
from settings.test import MEDIA_TEST
from tests.runner import init_database


@before.harvest
def initial_setup(server):
    call_command('syncdb', interactive=False, verbosity=0)
    call_command('flush', interactive=False, verbosity=0)
    try:
        call_command('migrate', interactive=False, verbosity=0)
    except Exception:
        pass
    # call_command('loaddata', 'all', verbosity=0)
    setup_test_environment()
    world.browser = Browser('chrome')

@after.harvest
def cleanup(server):
    connection.creation.destroy_test_db(settings.DATABASES['default']['NAME'])
    teardown_test_environment()

@before.each_scenario
def reset_data(scenario):
    # Clean up django.
    call_command('flush', interactive=False, verbosity=0)
    if os.path.exists(MEDIA_TEST):
        shutil.rmtree(MEDIA_TEST)

    os.mkdir(MEDIA_TEST)
    # init_database()
    # call_command('loaddata', 'all', verbosity=0)

@after.each_scenario
def delete_test_files(scenario):
    # eliminamos todos los archivos creados para el test
    shutil.rmtree(MEDIA_TEST)

@after.all
def teardown_browser(total):
    world.browser.quit()