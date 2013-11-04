# -*- coding: utf-8 -*-
import os
import urllib2
from lettuce import step, world
from lettuce.django import django_url
import simplejson
from services.models import Photo, CustomUser, Comment
from services.utils import S3BucketHandler
from settings.test import MEDIA_TEST, TEST_FIXTURES
from tests.factories import *
from settings.common import PROJECT_ROOT, BUCKET_URL
from tests.utils import client, saved_a_few_instances_ok, content_type_ok, saved_only_one_instance_ok, content_type_ok_ext


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
    step.behave_as("""Then I receive a JSON response on client""")

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
    picture_path = os.path.join(PROJECT_ROOT, 'tests', 'fixtures', 'imgs', 'test_img2.png')
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

@step(u'When I send POST request with photo data in JSON format')
def when_i_send_post_request_with_photo_data_in_json_format(step):
    json_file = open(os.path.join(TEST_FIXTURES, 'imagen_prueba_base64.json'))
    data = simplejson.load(json_file)
    world.resp = client.post('/api/v1/photo/', data=data)

@step(u'Given A few photos created')
def given_a_few_photos_created(step):
    PhotoFactory.create_batch(3)
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
    world.resp = client.get('/api/v1/photo/' + str(world.photo.id) + '/')

@step(u'And I can read the photo file referenced in the JSON object')
def and_i_can_read_the_photo_file_referenced_in_the_json_object(step):
    world.resp = client.get('/media/' + world.photo.img.url)
    assert content_type_ok('image/')

@step(u'And both files are uploaded to amazon s3 bucket')
def and_both_files_are_uploaded_to_amazon_s3_bucket(step):
    world.resp = urllib2.urlopen(BUCKET_URL + world.new_photo.img.name)
    assert content_type_ok_ext('image/')
    world.resp = urllib2.urlopen(BUCKET_URL + world.new_photo.get_img_p_name())
    assert content_type_ok_ext('image/')

@step(u'And both files are deleted from local server')
def and_both_files_are_deleted_from_local_server(step):
    path = os.path.join(MEDIA_TEST, 'photos',
                        'cat_' + str(world.new_photo.category.id),
                        'photo_' + str(world.new_photo.id))
    p_original = path + '.png'
    p_thumb = path + '.p.png'
    assert not os.path.exists(p_original)
    assert not os.path.exists(p_thumb)

    # al terminar el escenario borramos lo que hayamos subido de prueba al bucket
    b = S3BucketHandler()
    b.remove_file(world.new_photo.img.name)
    b.remove_file(world.new_photo.get_img_p_name())

@step(u'Given A photo created')
def given_a_photo_created(step):
    world.new_photo = PhotoFactory()

@step(u'And A few comments on this photo')
def and_a_few_comments_on_this_photo(step):
    world.comments = CommentFactory.create_batch(5, photo=world.new_photo)
    assert len(world.comments) == 5
    assert world.comments[0].pk is not None
    assert world.comments[4].pk is not None

@step(u'Then I receive comments counter as part of that JSON data')
def then_i_receive_comments_counter_as_part_of_that_json_data(step):
    dic = simplejson.loads(world.resp.content)
    assert dic['comments_count'] == 5

@step(u'When I send POST request with comment data in JSON format')
def when_i_send_post_request_with_comment_data_in_json_format(step):
    data = {
        "user": "/api/v1/user/1/",
        "photo": "/api/v1/photo/1/",
        "text": "This is a comment bla bla bla",
    }
    world.resp = client.post('/api/v1/comment/', data=data)

@step(u'Then New comment is created')
def then_new_comment_is_created(step):
    world.new_comment = Comment.objects.all().order_by('id').reverse()[0]
    assert world.new_comment.text == "This is a comment bla bla bla"
    assert world.new_comment.user == CustomUser.objects.get(pk=world.new_comment.user.id)
    assert world.new_comment.photo == Photo.objects.get(pk=world.new_comment.photo.id)
    assert world.new_comment.id is not None

@step(u'And Comment count is incremented by 1 in the commented photo')
def and_comment_count_is_incremented_by_1_in_the_commented_photo(step):
    resp = client.get('/api/v1/photo/1/')
    dic = simplejson.loads(resp.content)
    assert dic['comments_count'] == 1

@step(u'And Photo file is uploaded to amazon s3 bucket')
def and_photo_file_is_uploaded_to_amazon_s3_bucket(step):
    world.resp = urllib2.urlopen(BUCKET_URL + world.new_photo.img.name)
    assert content_type_ok_ext('image/')

@step(u'And Photo file is deleted from local server')
def and_photo_file_is_deleted_from_local_server(step):
    path = os.path.join(MEDIA_TEST, 'photos',
                            'cat_' + str(world.new_photo.category.id),
                            'photo_' + str(world.new_photo.id))
    p_original = path + '.png'
    assert not os.path.exists(p_original)

    # al terminar el escenario borramos lo que hayamos subido de prueba al bucket
    b = S3BucketHandler()
    b.remove_file(world.new_photo.img.name)

@step(u'Given a user with "([^"]*)":"([^"]*)"')
def given_a_user_with_group1_group2(step, group1, group2):
    world.user = CustomUserFactory(username=group1, password=group2)

@step(u'When i log in with user "([^"]*)":"([^"]*)"')
def when_i_log_in_with_user_group1_group2(step, group1, group2):
    world.resp = client.post('/api/v1/user/login/', data=[group1, group2])
    pass

@step(u'Then user is logged in')
def then_user_is_logged_in(step):
    assert False, 'This step must be implemented'
@step(u'Given a user with "([^"]*)":"([^"]*)":"([^"]*)"')
def given_a_user_with_group1_group2_group3(step, group1, group2, group3):
    assert False, 'This step must be implemented'
@step(u'Given an user logged in')
def given_an_user_logged_in(step):
    assert False, 'This step must be implemented'
@step(u'When i send GET request to logout url')
def when_i_send_get_request_to_logout_url(step):
    assert False, 'This step must be implemented'
@step(u'Then user is logged out')
def then_user_is_logged_out(step):
    assert False, 'This step must be implemented'


# @step(u'And both files are uploaded to amazon s3 bucket')
# def and_both_files_are_uploaded_to_amazon_s3_bucket(step):
#
#     world.resp = urllib2.urlopen(BUCKET_URL + world.new_photo.get_img_thumbnail_name())
#     assert content_type_ok_ext('image/')
#
# @step(u'And both files are deleted from local server')
# def and_both_files_are_deleted_from_local_server(step):
#     path = os.path.join(MEDIA_TEST, 'photos',
#                         'cat_' + str(world.new_photo.category.id),
#                         'photo_' + str(world.new_photo.id))
#     p_original = path + '.png'
#     p_thumb = path + '.p.png'
#     assert not os.path.exists(p_original)
#     assert not os.path.exists(p_thumb)
#
#     # al terminar el escenario borramos lo que hayamos subido de prueba al bucket
#     b = S3BucketHandler()
#     b.remove_file(world.new_photo.img.name)
#     b.remove_file(world.new_photo.get_img_thumbnail_name())