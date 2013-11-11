# -*- coding: utf-8 -*-
from django.test import TestCase
import simplejson
from tests.factories import CustomUserFactory
from tests.utils import client, API_BASE_URI
from tests.fixtures.input_data import *


class LoginTest(TestCase):
    """
        Prueba con campos correctamente escritos en el formulario de login.

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


class LoginFormValidationTest(TestCase):
    """
        Prueba con campos mal escritos en formulario de login.

        username_email ok, password FAIL
        username_email FAIL, password ok
        username_email FAIL, password FAIL
    """

    def __assert_invalid_form__(self, username, password):
        # WHEN
        data = simplejson.dumps({
            'username_email': username,
            'password': password,
            })
        resp = client.post(API_BASE_URI + 'user/login/', data=data, content_type='application/json')
        # THEN
        assert resp.status_code == 200
        resp_content = simplejson.loads(resp.content)
        assert resp_content['status'] == 'error'
        assert resp_content['reason_code'] == 3

    def test_with_valid_usernames_emails_and_invalid_passwords(self):
        for u in usernames_emails['valids']:
            for p in passwords['invalids']:
                self.__assert_invalid_form__(u, p)

    def test_with_invalid_usernames_emails_and_valid_passwords(self):
        for u in usernames_emails['invalids']:
            for p in passwords['valids']:
                self.__assert_invalid_form__(u, p)

    def test_with_invalid_usernames_emails_and_invalid_passwords(self):
        for u in usernames_emails['invalids']:
            for p in passwords['invalids']:
                self.__assert_invalid_form__(u, p)