from django.test import TestCase
import simplejson
from settings.common import API_BASE_URI
from tests.fixtures.input_data import username_email_list, password_list
from tests.testcase_classes import FormTestCase
from tests.utils import client


class LoginFormTest(FormTestCase):
    """
        Prueba con campos mal escritos en formulario de login.

        username_email ok, password invalid
        username_email invalid, password ok
        username_email invalid, password invalid
    """
    def _assert_invalid_login_form(self, username, password):
        # WHEN
        data = simplejson.dumps({
            'username_email': username,
            'password': password,
        })
        self.resp = client.post(API_BASE_URI + 'user/login/', data=data, content_type='application/json')
        # THEN
        self._assert_invalid_form()

    def test_with_valid_usernames_emails_and_invalid_passwords(self):
        for u in username_email_list['valids']:
            for p in password_list['invalids']:
                self._assert_invalid_login_form(u, p)

    def test_with_invalid_usernames_emails_and_valid_passwords(self):
        for u in username_email_list['invalids']:
            for p in password_list['valids']:
                self._assert_invalid_login_form(u, p)

    def test_with_invalid_usernames_emails_and_invalid_passwords(self):
        for u in username_email_list['invalids']:
            for p in password_list['invalids']:
                self._assert_invalid_login_form(u, p)