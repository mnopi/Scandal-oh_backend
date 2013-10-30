# # terrain.py
# import shutil
# from lettuce import before, after, world
# from splinter.browser import Browser
# from django.test.utils import setup_test_environment, teardown_test_environment
# from django.core.management import call_command
# from django.db import connection
# from settings.test import MEDIA_TEST
# from tests.utils import reset_media_test_folder
#
#
# @before.harvest
# def initial_setup(server):
#     call_command('syncdb', interactive=False, verbosity=0)
#     call_command('flush', interactive=False, verbosity=0)
#     try:
#         # si ya se ha migrado antes no hace falta volver a hacerlo
#         if 'services_customuser' not in connection.introspection.table_names():
#             call_command('migrate', interactive=False, verbosity=0)
#     except:
#         pass
#     # call_command('loaddata', 'all', verbosity=0)
#     setup_test_environment()
#     world.browser = Browser('chrome')
#
# @after.harvest
# def cleanup(server):
#     # connection.creation.destroy_test_db(settings.DATABASES['default']['NAME'])
#     teardown_test_environment()
#     world.browser.quit()
#
# @before.each_scenario
# def reset_data(scenario):
#     # Clean up database
#     call_command('flush', interactive=False, verbosity=0)
#     # Reset /media/test folder
#     reset_media_test_folder()
#     # init_database()
#     # call_command('loaddata', 'all', verbosity=0)
#
# @after.each_scenario
# def delete_test_files(scenario):
#     # eliminamos todos los archivos creados para el test
#     shutil.rmtree(MEDIA_TEST)
