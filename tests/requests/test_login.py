# -*- coding: utf-8 -*-
from django.test import TestCase
import simplejson
from tests.factories import CustomUserFactory
from tests.utils import client, API_BASE_URI


class LoginTest(TestCase):
    """
        username ok, password ok
        username ok, password FAIL
        email ok, password ok
        email ok, password FAIL
        email FAIL, password ok
        email FAIL, password FAIL
    """
    def test_login_with_username_ok_and_password_ok(self):
        # GIVEN
        user_password = '123456'
        user = CustomUserFactory(password=user_password)
        # WHEN
        data = simplejson.dumps({
            'username_email': user.username,
            'password': user_password,
        })
        resp = client.post(API_BASE_URI + 'user/login/', data=data, content_type='application/json')
        # THEN
        assert resp.status_code == 200
        resp_content = simplejson.loads(resp.content)
        assert resp_content['status'] == 'ok'
        assert resp_content['user_uri'] is not None

    def test_login_with_username_ok_and_password_fail(self):
        # GIVEN
        user_password = '123456'
        user = CustomUserFactory(password=user_password)
        # WHEN
        data = simplejson.dumps({
            'username_email': user.username,
            'password': '123456aaaa',
            })
        resp = client.post(API_BASE_URI + 'user/login/', data=data, content_type='application/json')
        # THEN
        assert resp.status_code == 200
        resp_content = simplejson.loads(resp.content)
        assert resp_content['status'] == 'error'
        assert resp_content['reason_code'] == 2

    def test_login_with_email_ok_and_password_ok(self):
        # GIVEN
        user_password = '123456'
        user = CustomUserFactory(email='yo@example.com', password=user_password)
        # WHEN
        data = simplejson.dumps({
            'username_email': user.email,
            'password': user_password,
            })
        resp = client.post(API_BASE_URI + 'user/login/', data=data, content_type='application/json')
        # THEN
        assert resp.status_code == 200
        resp_content = simplejson.loads(resp.content)
        assert resp_content['status'] == 'ok'
        assert resp_content['user_uri'] is not None

    def test_login_with_email_ok_and_password_fail(self):
        # GIVEN
        user_password = '123456'
        user = CustomUserFactory(email='yo@example.com', password=user_password)
        # WHEN
        data = simplejson.dumps({
            'username_email': user.email,
            'password': '123456aaaa',
            })
        resp = client.post(API_BASE_URI + 'user/login/', data=data, content_type='application/json')
        # THEN
        assert resp.status_code == 200
        resp_content = simplejson.loads(resp.content)
        assert resp_content['status'] == 'error'
        assert resp_content['reason_code'] == 2

    def test_login_with_email_fail_and_password_ok(self):
        # GIVEN
        user_password = '123456'
        user = CustomUserFactory(email='yo@example.com', password=user_password)
        # WHEN
        data = simplejson.dumps({
            'username_email': 'yono@yo.com',
            'password': user_password,
            })
        resp = client.post(API_BASE_URI + 'user/login/', data=data, content_type='application/json')
        # THEN
        assert resp.status_code == 200
        resp_content = simplejson.loads(resp.content)
        assert resp_content['status'] == 'error'
        assert resp_content['reason_code'] == 1

    def test_login_with_email_fail_and_password_fail(self):
        # GIVEN
        user_password = '123456'
        user = CustomUserFactory(email='yo@example.com', password=user_password)
        # WHEN
        data = simplejson.dumps({
            'username_email': 'yono@yo.com',
            'password': '123456aaa',
            })
        resp = client.post(API_BASE_URI + 'user/login/', data=data, content_type='application/json')
        # THEN
        assert resp.status_code == 200
        resp_content = simplejson.loads(resp.content)
        assert resp_content['status'] == 'error'
        assert resp_content['reason_code'] == 1