# -*- coding: utf-8 -*-
import os
from lettuce import step, world
from lettuce.django import django_url
import simplejson
from services.models import Photo
from settings.test import MEDIA_TEST, TEST_FIXTURES
from tests.factories import *
from settings.common import PROJECT_ROOT
from tests.utils import client


@step(u'Given A user created with username "([^"]*)" and password "([^"]*)"')
def given_a_user_created_with_username_group1_and_password_group2(step, group1, group2):
    world.user = CustomUserFactory(username=group1, password=group2)

@step(u'And A photo category created with name "([^"]*)"')
def and_a_photo_category_created_with_name_group1(step, group1):
    world.category = CategoryFactory(name=group1)

@step(u'When I go to "([^"]*)" URL')
def when_i_go_to_group1_url(step, group1):
    world.browser.visit(django_url(group1))

@step(u'And I attach a file to photo form')
def and_i_attach_a_file_to_photo_form(step):
    picture_path = os.path.join(PROJECT_ROOT, 'tests', 'imgs', 'test_img.png')
    world.browser.attach_file('img', picture_path)

@step(u'And I fill in "([^"]*)" with "([^"]*)"')
def and_i_fill_in_group1_with_group2(step, group1, group2):
    world.browser.fill(group1, group2)

@step(u'And I press the "([^"]*)" button')
def and_i_press_the_group1_button(step, group1):
    world.browser.find_by_css('input[type="submit"]').click()

@step(u'Then New photo is created')
def then_new_photo_is_created(step):
    photos = Photo.objects.all()
    assert len(photos) == 1
    assert photos[0].id == 1

@step(u'And Photo file is uploaded')
def and_photo_file_is_uploaded(step):
    assert os.path.exists(os.path.join(MEDIA_TEST, 'photos', 'cat_1', 'photo_1.png'))


@step(u'When I send POST request with photo data in JSON format')
def when_i_send_post_request_with_photo_data_in_json_format(step):
    json_file = open(os.path.join(TEST_FIXTURES, 'imagen_prueba_base64.json'))
    data = simplejson.load(json_file)
    world.resp = client.post('/api/v1/photo/', data=data)

@step(u'And I receive an JSON response on client')
def and_i_receive_an_json_response(step):
    assert world.resp.status_code == 201
    assert world.resp._headers['content-type'][1] == 'application/json'
    assert world.resp.content != ''