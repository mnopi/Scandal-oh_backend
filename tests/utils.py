from lettuce import world
from tastypie.test import TestApiClient


def saved_only_one_instance_ok(instance_class):
    "Comprueba si se ha guardado una sola instancia para esa clase en BD"
    instances = instance_class.objects.all()
    return len(instances) == 1 and instances[0].id is not None


def saved_a_few_instances_ok(instance_class):
    "Comprueba si se ha guardado una sola instancia para esa clase en BD"
    instances = instance_class.objects.all()
    return len(instances) > 1 and instances[1].id is not None


def content_type_ok(content_type):
    return content_type in world.resp._headers['content-type'][1]


def content_type_ok_ext(content_type):
    """
    Muestra el tipo de contenido de una respuesta que viene desde
    un servidor externo
    """
    return world.resp.code == 200 \
        and content_type in world.resp.headers.dict['content-type']


client = TestApiClient()