# -*- coding: utf-8 -*-

from django.test import TestCase
import simplejson
from tests.factories import CustomUserFactory
from tests.utils import client, API_BASE_URI


class RegisterTest(TestCase):
    existing_username = 'paco33'
    existing_email = 'manitobueno@example.com'
    another_username = 'capitancock'
    another_username_invalid = 'capitañooo'
    another_email = 'yupi@yo.com'
    another_email_invalid = 'yupi@.com'
    password = 'manito666'
    password_invalid = 'mani'

    @classmethod
    def setUpClass(cls):
        # GIVEN
        cls.existing_user = CustomUserFactory(
            username=cls.existing_username,
            password=cls.password,
            email=cls.existing_email,
        )

    def __assert_error__(self, data):
        # WHEN
        self.resp = client.post(API_BASE_URI + 'user/',
                                data=simplejson.dumps(data),
                                content_type='application/json')
        # THEN
        assert self.resp.status_code == 200
        resp_content = simplejson.loads(self.resp.content)
        assert resp_content['status'] == 'error'

    def test_register_ok(self):
        # WHEN
        data = {
            'username': self.another_username,
            'email': self.another_email,
            'password': self.password,
        }
        self.resp = client.post(API_BASE_URI + 'user/',
                                data=simplejson.dumps(data),
                                content_type='application/json')
        # THEN
        assert self.resp.status_code == 201
        resp_content = simplejson.loads(self.resp.content)
        assert resp_content['id'] is not None

    def test_register_with_existing_username(self):
        data = {
            'username': self.existing_username,
            'email': self.another_email,
            'password': self.password,
        }
        self.__assert_error__(data)

    def test_register_with_existing_email(self):
        data = {
            'username': self.another_username,
            'email': self.existing_email,
            'password': self.password,
        }
        self.__assert_error__(data)

    def test_register_with_invalid_username(self):
        data = {
            'username': self.another_username_invalid,
            'email': self.another_email,
            'password': self.password,
        }
        self.__assert_error__(data)

    def test_register_with_invalid_email(self):
        data = {
            'username': self.another_username,
            'email': self.another_email_invalid,
            'password': self.password,
            }
        self.__assert_error__(data)

    def test_register_with_invalid_password(self):
        data = {
            'username': self.another_username,
            'email': self.another_email,
            'password': self.password_invalid,
            }
        self.__assert_error__(data)
