# -*- coding: utf-8 -*-

from django.test import TestCase
import simplejson
from tests.factories import CustomUserFactory
from tests.utils import client, API_BASE_URI


class RegisterTest(TestCase):
    existing_username = 'paco33'
    existing_email = 'manitobueno@example.com'
    another_username = 'capitancock'
    another_email = 'yupi@yo.com'
    password = 'mani'

    @classmethod
    def setUpClass(cls):
        # GIVEN
        cls.existing_user = CustomUserFactory(
            username=cls.existing_username,
            password=cls.password,
            email=cls.existing_email,
        )

    def test_register_ok(self):
        pass

    def test_register_with_existing_username(self):
        # WHEN
        data = simplejson.dumps({
            'username': self.existing_username,
            'email': self.another_email,
            'password': self.password,
        })
        resp = client.post(API_BASE_URI + 'user/', data=data, content_type='application/json')
        # THEN
        assert resp.status_code == 200
        resp_content = simplejson.loads(resp.content)
        assert resp_content['status'] == 'error'

    def test_register_with_existing_email(self):
        # WHEN
        data = simplejson.dumps({
            'username': self.another_username,
            'email': self.existing_email,
            'password': self.password,
            })
        resp = client.post(API_BASE_URI + 'user/', data=data, content_type='application/json')
        # THEN
        assert resp.status_code == 200
        resp_content = simplejson.loads(resp.content)
        assert resp_content['status'] == 'error'