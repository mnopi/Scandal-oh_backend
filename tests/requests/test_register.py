# -*- coding: utf-8 -*-

from django.test import TestCase
import simplejson
from tests.factories import CustomUserFactory, FacebookUserFactory
from tests.utils import client, API_BASE_URI


class RegisterTest(TestCase):
    username = {
        'existing': 'paco33',
        'existing_facebook': 'paco33_facebook',
        'another': 'capitancock',
        'another_facebook': 'capitancock_facebook',
        'invalid': 'capitañooo',
    }
    email = {
        'existing': 'manitobueno@example.com',
        'existing_facebook': 'manitobueno_facebook@example.com',
        'another': 'yupi@yo.com',
        'another_facebook': 'yupi_facebook@yo.com',
        'invalid': 'yupi@.com',
    }
    password = 'manito666'
    password_invalid = 'mani'

    @classmethod
    def setUpClass(cls):
        # GIVEN
        cls.existing_user = CustomUserFactory(
            username=cls.username['existing'],
            email=cls.email['existing'],
            password=cls.password,
        )
        cls.existing_facebook_user = FacebookUserFactory(
            username=cls.username['existing_facebook'],
            email=cls.email['existing_facebook'],
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
            'username': self.username['another'],
            'email': self.email['another'],
            'password': self.password,
        }
        self.__assert_ok__()

    def test_register_ok_with_facebook(self):
        self.data = {
            'username': self.username['another_facebook'],
            'email': self.email['another_facebook'],
            'social_network': 1,
        }
        self.__assert_ok__()
        assert self.resp_content['social_network'] == 1

    #
    # CASOS DE FALLO
    #

    def test_register_with_existing_username(self):
        self.data = {
            'username': self.username['existing'],
            'email': self.email['another'],
            'password': self.password,
        }
        self.__assert_error__()

    def test_register_with_existing_email(self):
        self.data = {
            'username': self.username['another'],
            'email': self.email['existing'],
            'password': self.password,
        }
        self.__assert_error__()

    def test_register_with_invalid_username(self):
        self.data = {
            'username': self.username['invalid'],
            'email': self.email['another'],
            'password': self.password,
        }
        self.__assert_error__()

    def test_register_with_invalid_email(self):
        self.data = {
            'username': self.username['another'],
            'email': self.email['invalid'],
            'password': self.password,
        }
        self.__assert_error__()

    def test_register_with_invalid_password(self):
        self.data = {
            'username': self.username['another'],
            'email': self.email['another'],
            'password': self.password_invalid,
        }
        self.__assert_error__()
