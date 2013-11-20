from django.test import LiveServerTestCase, TestCase
import simplejson
from splinter import Browser
from settings import common
from settings.common import API_BASE_URI
from tests.utils import client


class SplinterTestCase(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        cls.browser = Browser('chrome')
        super(SplinterTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(SplinterTestCase, cls).tearDownClass()


class UnitTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        common.UNIT_TEST_MODE = True
        super(UnitTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        common.UNIT_TEST_MODE = False
        super(UnitTestCase, cls).tearDownClass()


class RequestTestCase(TestCase):
    def setUp(self):
        self.resp_obj = None

    # ASSERTIONS

    def _assert_error_response(self):
        assert self.resp.status_code == 200
        self._set_resp_obj()
        assert self.resp_obj['status'] == 'error'

    def _assert_get_ok(self):
        assert self.resp.status_code == 200
        self._set_resp_obj()

    def _assert_post_ok_200(self):
        assert self.resp.status_code == 200
        self._set_resp_obj()

    def _assert_post_ok_201(self):
        assert self.resp.status_code == 201
        self._set_resp_obj()

    def _assert_put_ok(self):
        self._assert_get_ok()

    def _assert_delete_ok(self):
        assert self.resp.status_code == 204

    def _assert_resp_obj_has_length(self, length):
        assert len(self.resp_obj) == length

    def _assert_resp_obj_has_key_str(self, attr):
        assert self.resp_obj[attr] is str

    def _assert_resp_obj_has_key_not_none(self, attr):
        assert self.resp_obj[attr] is not None

    def _assert_resp_obj_has_key_equals_to(self, attr, value):
        assert self.resp_obj[attr] == value

    # REQUEST OPERATIONS

    def _post(self, data):
        self.resp = client.post(
            API_BASE_URI + '%s/' % self.resource_name,
            data=simplejson.dumps(data),
            content_type='application/json'
        )

    def _get_list(self):
        self.resp = client.get(API_BASE_URI + '%s/' % self.resource_name)

    def _get_element(self, pk):
        self.resp = client.get(API_BASE_URI + '%s/%i/' % (self.resource_name, pk))

    def _put(self, pk, data):
        self.resp = client.put(
            API_BASE_URI + '%s/%i/' % (self.resource_name, pk),
            data=simplejson.dumps(data),
            content_type='application/json'
        )

    def _delete(self, pk):
        self.resp = client.delete(API_BASE_URI + '%s/%i/' % (self.resource_name, pk))

    def _set_resp_obj(self):
        """Deserializa el objeto JSON devuelto en la respuesta"""
        obj = simplejson.loads(self.resp.content)
        self.resp_obj = obj['objects'] if 'objects' in obj else obj


class FormTestCase(TestCase):
    def _assert_invalid_form(self):
        # THEN
        assert self.resp.status_code == 200
        resp_content = simplejson.loads(self.resp.content)
        assert resp_content['status'] == 'error'
        assert resp_content['reason_code'] == 3