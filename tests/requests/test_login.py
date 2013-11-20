# -*- coding: utf-8 -*-
from django.test import TestCase
import simplejson
from settings.common import API_BASE_URI
from tests.factories import CustomUserFactory, FacebookUserFactory
from tests.testcase_classes import RequestTestCase
from tests.utils import client
from tests.fixtures.input_data import *


class LoginTest(RequestTestCase):
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

    def _assert_login_ok(self):
        # WHEN
        self.resp = client.post(API_BASE_URI + 'user/login/',
                                data=simplejson.dumps(self.data),
                                content_type='application/json')
        # THEN
        self._assert_post_ok_200()
        assert self.resp_obj['status'] == 'ok'
        assert type(self.resp_obj['user_uri']) is str and self.resp_obj['user_uri'] != ''

    def _assert_login_failed(self):
        # WHEN
        self.resp = client.post(API_BASE_URI + 'user/login/',
                                data=simplejson.dumps(self.data),
                                content_type='application/json')
        # THEN
        self._assert_error_response()

    def _assert_error_with_invalid_username_email(self):
        self._assert_login_failed()
        assert self.resp_obj['reason_code'] == 1

    def _assert_error_with_invalid_password(self):
        self._assert_login_failed()
        assert self.resp_obj['reason_code'] == 2

    def test_login_with_username_ok_and_password_ok(self):
        self.data = {
            'username_email': username['existing'],
            'password': password,
        }
        self._assert_login_ok()

    def test_login_with_email_ok_and_password_ok(self):
        self.data = {
            'username_email': email['existing'],
            'password': password,
            }
        self._assert_login_ok()

    def test_login_with_facebook_ok(self):
        self.data = {
            'username': username['existing_facebook'],
            'email': email['existing_facebook'],
            'social_network': 1,
        }
        self._assert_login_ok()

    def test_login_with_username_ok_and_password_fail(self):
        self.data = {
            'username_email': username['existing'],
            'password': password_fail,
        }
        self._assert_error_with_invalid_password()

    def test_login_with_email_ok_and_password_fail(self):
        self.data = {
            'username_email': email['existing'],
            'password': password_fail,
        }
        self._assert_error_with_invalid_password()

    def test_login_with_email_fail_and_password_ok(self):
        self.data = {
            'username_email': email['another'],
            'password': password,
        }
        self._assert_error_with_invalid_username_email()

    def test_login_with_email_fail_and_password_fail(self):
        self.data = {
            'username_email': email['another'],
            'password': password,
        }
        self._assert_error_with_invalid_username_email()

    def test_normal_login_failed_from_facebook_user(self):
        """Login normal desde un usuario que fue creado con facebook"""
        # given
        u = FacebookUserFactory()
        # when
        self.data = {
            'username_email': u.username,
            'password': '123456',
            }
        # then
        self._assert_error_with_invalid_password()




