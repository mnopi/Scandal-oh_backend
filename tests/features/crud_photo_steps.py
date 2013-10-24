# -*- coding: utf-8 -*-
import os
from lettuce import step, world
from lettuce.django import django_url
import simplejson
from services.models import Photo
from settings.test import MEDIA_TEST, TEST_FIXTURES
from tests.factories import *
from settings.common import PROJECT_ROOT
from tests.utils import client, saved_a_few_instances_ok, content_type_ok


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
    picture_path = os.path.join(PROJECT_ROOT, 'tests', 'fixtures', 'imgs', 'test_img.png')
    world.browser.attach_file('img', picture_path)

@step(u'And I fill in "([^"]*)" with "([^"]*)"')
def and_i_fill_in_group1_with_group2(step, group1, group2):
    world.browser.fill(group1, group2)

@step(u'And I press the "([^"]*)" button')
def and_i_press_the_group1_button(step, group1):
    world.browser.find_by_css('input[type="submit"]').click()

@step(u'Then New photo is created with title "([^"]*)"')
def then_new_photo_is_created_with_title(step,group1):
    world.new_photo = Photo.objects.all().order_by('id').reverse()[0]
    assert world.new_photo.title == group1
    assert world.new_photo.id is not None

@step(u'And Photo file is uploaded')
def and_photo_file_is_uploaded(step):
    path = os.path.join(MEDIA_TEST, 'photos',
                        'cat_' + str(world.new_photo.category.id),
                        'photo_' + str(world.new_photo.id) + '.png')
    assert os.path.exists(path)


@step(u'When I send POST request with photo data in JSON format')
def when_i_send_post_request_with_photo_data_in_json_format(step):
    json_file = open(os.path.join(TEST_FIXTURES, 'imagen_prueba_base64.json'))
    data = simplejson.load(json_file)
    world.resp = client.post('/api/v1/photo/', data=data)

@step(u'Given A few photos created')
def given_a_few_photos_created(step):
    for x in range(0, 2):
        PhotoFactory()
    saved_a_few_instances_ok(Photo)

@step(u'When I send GET request on photo list URL')
def when_i_send_get_request_on_photo_list_url(step):
    world.resp = client.get('/api/v1/photo/')

@step(u'Then I receive an JSON response on client')
def then_i_receive_an_json_response_on_client(step):
    step.behave_as("""And I receive an JSON response on client""")


@step(u'And The response status code is from "([^"]*)" request')
def and_the_response_status_code_is_from_group1_request(step, group1):
    if group1 == 'POST':
        assert world.resp.status_code == 201
    elif group1 == 'GET':
        assert world.resp.status_code == 200

@step(u'Then I receive a JSON response on client')
def then_i_receive_a_json_response_on_client(step):
    assert world.resp._headers['content-type'][1] == 'application/json'
    assert world.resp.content != ''

@step(u'When I send GET request to read a concrete photo in JSON format')
def when_i_send_get_request_to_read_a_concrete_photo_in_json_format(step):
    world.photo = Photo.objects.get(id=1)
    client.get('/api/v1/photo/' + str(world.photo.id) + '/')

@step(u'And I can read the photo file referenced in the JSON object')
def and_i_can_read_the_photo_file_referenced_in_the_json_object(step):
    world.resp = client.get(world.photo.img.url)
    assert content_type_ok('image/')

@step(u'And Photo thumbnail file is uploaded with .p.png extension')
def and_photo_thumbnail_file_is_uploaded_with_p_png_extension(step):
    path = os.path.join(MEDIA_TEST, 'photos',
                        'cat_' + str(world.new_photo.category.id),
                        'photo_' + str(world.new_photo.id) + '.p.png')
    assert os.path.exists(path)