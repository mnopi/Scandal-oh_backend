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


#
# VALIDATION
#

def validation_username(username, password):
    # GIVEN
    user = CustomUserFactory(username=username, password=password)
    # WHEN
    data = simplejson.dumps({
        'username_email': username,
        'password': password,
        })
    validation(user, data)


def validation_email(email, password):
    # GIVEN
    user = CustomUserFactory(email=email, password=password)
    # WHEN
    data = simplejson.dumps({
        'username_email': email,
        'password': password,
        })
    validation(user, data)


def validation(user, data):
    resp = client.post(API_BASE_URI + 'user/login/', data=data, content_type='application/json')
    # THEN
    assert resp.status_code == 200
    resp_content = simplejson.loads(resp.content)
    assert resp_content['status'] == 'error'
    assert resp_content['reason_code'] == 3
    user.delete()


class ValidFormLoginTest(TestCase):
    """
        Prueba con campos mal escritos en formulario de login.

        username ok, password FAIL
        username FAIL, password ok
        username FAIL, password FAIL
        email ok, password FAIL
        email FAIL, password ok
        email FAIL, password FAIL
    """
    def test_login_validation_with_ok_usernames_and_fail_passwords(self):
        for u in valid_usernames:
            for p in invalid_passwords:
                validation_username(u, p)

    def test_login_validation_with_fail_usernames_and_ok_passwords(self):
        for u in invalid_usernames:
            for p in valid_passwords:
                validation_username(u, p)

    def test_login_validation_with_fail_usernames_and_fail_passwords(self):
        for u in invalid_usernames:
            for p in invalid_passwords:
                validation_username(u, p)

    def test_login_validation_with_ok_emails_and_fail_passwords(self):
        for u in valid_emails:
            for p in invalid_passwords:
                validation_email(u, p)

    def test_login_validation_with_fail_emails_and_ok_passwords(self):
        for u in invalid_emails:
            for p in valid_passwords:
                validation_email(u, p)

    def test_login_validation_with_fail_emails_and_fail_passwords(self):
        for u in invalid_emails:
            for p in invalid_passwords:
                validation_email(u, p)
