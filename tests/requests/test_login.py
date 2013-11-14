# -*- coding: utf-8 -*-
from django.test import TestCase
import simplejson
from settings.common import API_BASE_URI
from tests.factories import CustomUserFactory, FacebookUserFactory
from tests.utils import client
from tests.fixtures.input_data import *


class LoginTest(TestCase):
    """
        Prueba con campos correctamente escritos en el formulario de login.

        username ok, password ok
        email ok, password ok
        fb -> username ok, email ok
        username ok, password FAIL
        email ok, password FAIL
        email FAIL, password ok
        email FAIL, password FAIL
    """
    def setUp(self):
        # GIVEN
        self.existing_user = CustomUserFactory(
            username=username['existing'],
            email=email['existing'],
            password=password,
            )
        self.existing_facebook_user = FacebookUserFactory(
            username=username['existing_facebook'],
            email=email['existing_facebook'],
            )

    def __assert_ok__(self):
        # WHEN
        self.resp = client.post(API_BASE_URI + 'user/login/',
                                data=simplejson.dumps(self.data),
                                content_type='application/json')
        # THEN
        assert self.resp.status_code == 200
        self.resp_content = simplejson.loads(self.resp.content)
        assert self.resp_content['status'] == 'ok'
        assert self.resp_content['user_uri'] is not None
        assert type(self.resp_content['user_uri']) is str

    def __assert_error__(self):
        # WHEN
        self.resp = client.post(API_BASE_URI + 'user/login/',
                                data=simplejson.dumps(self.data),
                                content_type='application/json')
        # THEN
        assert self.resp.status_code == 200
        self.resp_content = simplejson.loads(self.resp.content)
        assert self.resp_content['status'] == 'error'

    def __assert_error_with_invalid_username_email__(self):
        self.__assert_error__()
        assert self.resp_content['reason_code'] == 1

    def __assert_error_with_invalid_password__(self):
        self.__assert_error__()
        assert self.resp_content['reason_code'] == 2

    def test_login_with_username_ok_and_password_ok(self):
        self.data = {
            'username_email': username['existing'],
            'password': password,
        }
        self.__assert_ok__()

    def test_login_with_email_ok_and_password_ok(self):
        self.data = {
            'username_email': email['existing'],
            'password': password,
            }
        self.__assert_ok__()

    def test_login_with_facebook_ok(self):
        "Prueba login desde facebook"
        self.data = {
            'username': username['existing_facebook'],
            'email': email['existing_facebook'],
            'social_network': 1,
        }
        self.__assert_ok__()

    def test_login_with_username_ok_and_password_fail(self):
        self.data = {
            'username_email': username['existing'],
            'password': password_fail,
        }
        self.__assert_error_with_invalid_password__()

    def test_login_with_email_ok_and_password_fail(self):
        self.data = {
            'username_email': email['existing'],
            'password': password_fail,
        }
        self.__assert_error_with_invalid_password__()

    def test_login_with_email_fail_and_password_ok(self):
        self.data = {
            'username_email': email['another'],
            'password': password,
        }
        self.__assert_error_with_invalid_username_email__()

    def test_login_with_email_fail_and_password_fail(self):
        self.data = {
            'username_email': email['another'],
            'password': password,
        }
        self.__assert_error_with_invalid_username_email__()


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
        for u in username_email_list['valids']:
            for p in password_list['invalids']:
                self.__assert_invalid_form__(u, p)

    def test_with_invalid_usernames_emails_and_valid_passwords(self):
        for u in username_email_list['invalids']:
            for p in password_list['valids']:
                self.__assert_invalid_form__(u, p)

    def test_with_invalid_usernames_emails_and_invalid_passwords(self):
        for u in username_email_list['invalids']:
            for p in password_list['invalids']:
                self.__assert_invalid_form__(u, p)