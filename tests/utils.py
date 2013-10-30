import os
import shutil
import urllib2
from django.test.client import Client
from lettuce import world
from tastypie.test import TestApiClient
from settings.common import PROJECT_ROOT, BUCKET_URL
from settings.test import MEDIA_TEST


def saved_only_one_instance_ok(instance_class):
    "Comprueba si se ha guardado una sola instancia para esa clase en BD"
    instances = instance_class.objects.all()
    return len(instances) == 1 and instances[0].id is not None


def saved_a_few_instances_ok(instance_class):
    "Comprueba si se ha guardado una sola instancia para esa clase en BD"
    instances = instance_class.objects.all()
    return len(instances) > 1 and instances[1].id is not None


def content_type_ok_ext(resp, content_type):
    """
    Muestra el tipo de contenido de una respuesta que viene desde
    un servidor externo (usando urllib)

    http://stackoverflow.com/questions/4843158/check-if-a-python-list-item-contains-a-string-inside-another-string
    """
    return resp.code == 200 and \
           len([s for s in resp.headers.headers if "Content-Type: " + content_type in s]) != 0


# client = TestApiClient()
client = Client()

API_BASE_URI = '/api/v1/'
TEST_IMGS_PATH = os.path.join(PROJECT_ROOT, 'tests', 'fixtures', 'imgs')


def get_file_from_bucket(file_id):
    return urllib2.urlopen(BUCKET_URL + file_id)


def reset_media_test_folder():
    if os.path.exists(MEDIA_TEST):
        shutil.rmtree(MEDIA_TEST)
    os.mkdir(MEDIA_TEST)