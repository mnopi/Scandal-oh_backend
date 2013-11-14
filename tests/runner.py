from django.contrib.auth.models import Group
from django.core.management import call_command
from django.db import connection
from django.test import LiveServerTestCase, TestCase
from django_nose import NoseTestSuiteRunner
from splinter import Browser
from settings import common
from tests.utils import reset_media_test_folder


def init_database():
    Group.objects.create(name='enclosure_owners')
    Group.objects.create(name='shop_owners')


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


class MyTestRunner(NoseTestSuiteRunner):
    def setup_databases(self, **kwargs):
        o = super(MyTestRunner, self).setup_databases()
        # init_database()
        return o

    def setup_test_environment(self, **kwargs):
        super(MyTestRunner, self).setup_test_environment()
        reset_media_test_folder()

    def teardown_test_environment(self):
        super(MyTestRunner, self).teardown_test_environment()
        reset_media_test_folder()