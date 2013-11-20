# -*- coding: utf-8 -*-

from django.test import TestCase
import requests
import simplejson
from settings.common import API_BASE_URI
from tests.factories import CustomUserFactory, FacebookUserFactory
from tests.utils import client
from tests.fixtures.input_data import *


class RegisterTest(TestCase):
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
        self.resp = client.post(API_BASE_URI + 'user/',
                                data=simplejson.dumps(self.data),
                                content_type='application/json')
        # THEN
        assert self.resp.status_code == 201
        self.resp_content = simplejson.loads(self.resp.content)
        assert self.resp_content['id'] is not None
        assert self.resp_content['status'] == 'ok'

    def __assert_error__(self):
        # WHEN
        self.resp = client.post(API_BASE_URI + 'user/',
                                data=simplejson.dumps(self.data),
                                content_type='application/json')
        # THEN
        assert self.resp.status_code == 200
        resp_content = simplejson.loads(self.resp.content)
        assert resp_content['status'] == 'error'

    #
    # CASOS DE ÉXITO
    #

    def test_register_ok(self):
        self.data = {
            'username': username['another'],
            'email': email['another'],
            'password': password,
        }
        self.__assert_ok__()

    def test_register_ok_with_facebook(self):
        self.data = {
            'username': username['another_facebook'],
            'email': email['another_facebook'],
            'social_network': 1,
        }
        self.__assert_ok__()
        assert self.resp_content['social_network'] == 1

    #
    # CASOS DE FALLO
    #

    def test_register_with_existing_username(self):
        self.data = {
            'username': username['existing'],
            'email': email['another'],
            'password': password,
        }
        self.__assert_error__()

    def test_register_with_existing_email(self):
        self.data = {
            'username': username['another'],
            'email': email['existing'],
            'password': password,
        }
        self.__assert_error__()

    def test_register_with_invalid_username(self):
        for u in username_list['invalids']:
            self.data = {
                'username': u,
                'email': email['another'],
                'password': password,
            }
            self.__assert_error__()

    def test_register_with_invalid_email(self):
        for e in email_list['invalids']:
            self.data = {
                'username': username['another'],
                'email': e,
                'password': password,
            }
            self.__assert_error__()

    def test_register_with_invalid_password(self):
        for p in password_list['invalids']:
            self.data = {
                'username': username['another'],
                'email': email['another'],
                'password': p,
            }
            self.__assert_error__()

    def test_register_with_invalid_all(self):
        self.data = {
            'username': username['invalid'],
            'email': email['invalid'],
            'password': password_invalid,
        }
        self.__assert_error__()
