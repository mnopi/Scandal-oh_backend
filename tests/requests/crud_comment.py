# # -*- coding: utf-8 -*-
from django.test import TestCase
import simplejson
from services.models import *
from tests.factories import *

from tests.runner import SplinterTestCase
from tests.utils import client, API_BASE_URI


class CrudCommentTest(TestCase):
    def test_create_comment(self):
        # given
        PhotoFactory.create_batch(2)
        # when
        data = simplejson.dumps({
            "user": "/api/v1/user/1/",
            "photo": "/api/v1/photo/1/",
            "text": "This is a comment bla bla bla"
        })
        resp = client.post(API_BASE_URI + 'comment/', data=data, content_type='application/json')
        # then
        assert resp.status_code == 201
        new_comment = Comment.objects.all().order_by('id').reverse()[0]
        assert new_comment.text == "This is a comment bla bla bla"
        assert new_comment.user == CustomUser.objects.get(pk=new_comment.user.id)
        assert new_comment.photo == Photo.objects.get(pk=new_comment.photo.id)
        assert new_comment.id is not None

    def test_read_comment_list(self):
        # given
        CommentFactory.create_batch(2)
        # when
        resp = client.get(API_BASE_URI + 'comment/')
        # then
        assert resp.status_code == 200
        assert len(simplejson.loads(resp.content)['objects']) == 2

    def test_read_comment(self):
        # given
        CommentFactory()
        # when
        resp = client.get(API_BASE_URI + 'comment/1/')
        # then
        assert resp.status_code == 200
        assert simplejson.loads(resp.content)['photo'] is not None

    def test_update_comment(self):
        # given
        CommentFactory(text='comment original blahblah')
        # when
        data = simplejson.dumps({
            'text': 'comment edited!!'
        })
        resp = client.put(API_BASE_URI + 'comment/1/', data=data, content_type='application/json')
        # then
        assert resp.status_code == 200
        assert simplejson.loads(resp.content)['text'] == 'comment edited!!'

    def test_delete_comment(self):
        # given
        CommentFactory()
        # when
        resp = client.delete(API_BASE_URI + 'comment/1/')
        # then
        assert resp.status_code == 204
        assert Comment.objects.all().count() == 0

