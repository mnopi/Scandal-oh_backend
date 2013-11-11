# -*- coding: utf-8 -*-
from django.test import TestCase
import simplejson
from services.models import *
from tests.factories import *

from tests.runner import SplinterTestCase
from tests.utils import client, API_BASE_URI


class CrudUserTest(TestCase):
    def __assert_created_ok__(self, data):
        resp = client.post(API_BASE_URI + 'user/', data=simplejson.dumps(data),
                           content_type='application/json')
        # then
        assert resp.status_code == 201
        new_user = CustomUser.objects.all().order_by('id').reverse()[0]
        assert new_user.id is not None

    def test_create_user_(self):
        # when
        data = {
            "username": "paco33",
            "password": "123456",
            "email": "tito@lalala.com"
        }
        self.__assert_created_ok__(data)

    def test_create_user_from_social_network(self):
        # when
        data = {
            "username": "paco33",
            "email": "tito@lalala.com",
            "social_network": 1,
        }
        self.__assert_created_ok__(data)

    def test_read_user_list(self):
        # given
        CustomUserFactory.create_batch(2)
        # when
        resp = client.get(API_BASE_URI + 'user/')
        # then
        assert resp.status_code == 200
        assert len(simplejson.loads(resp.content)['objects']) == 2

    def test_read_user(self):
        # given
        CustomUserFactory()
        # when
        resp = client.get(API_BASE_URI + 'user/1/')
        # then
        assert resp.status_code == 200
        assert simplejson.loads(resp.content)['username'] is not None

    def test_update_user(self):
        # given
        CustomUserFactory(email='original@yo.com')
        # when
        email_edited = 'edited@yo.com'
        data = simplejson.dumps({'email': email_edited})
        resp = client.put(API_BASE_URI + 'user/1/', data=data, content_type='application/json')
        # then
        assert resp.status_code == 200
        assert simplejson.loads(resp.content)['email'] == email_edited

    def test_delete_user(self):
        # given
        CustomUserFactory()
        # when
        resp = client.delete(API_BASE_URI + 'user/1/')
        # then
        assert resp.status_code == 204
        assert CustomUser.objects.all().count() == 0
