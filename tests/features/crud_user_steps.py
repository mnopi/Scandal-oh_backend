# -*- coding: utf-8 -*-
from lettuce import step, world
from services.models import CustomUser
from tests.utils import saved_only_one_instance_ok, client


@step(u'When I send POST request with user data in JSON format')
def when_i_send_post_request_with_user_data_in_json_format(step):
    data = {
        "username": "user001",
        "password": "12341231312",
        "email": "tito@lalala.com"
    }
    world.resp = client.post('/api/v1/user/', data=data)

@step(u'Then New user is created')
def then_new_user_is_created(step):
    assert saved_only_one_instance_ok(CustomUser)

@step(u'And I receive a JSON response')
def and_i_receive_a_json_response(step):
    step.behave_as("""Then I receive a JSON response on client""");