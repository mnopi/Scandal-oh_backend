from django.contrib.auth.models import Group
from django.test import LiveServerTestCase
from django_nose import NoseTestSuiteRunner
from splinter import Browser


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


# class MyTestRunner(DjangoTestSuiteRunner):
class MyTestRunner(NoseTestSuiteRunner):
    def setup_databases(self, **kwargs):
        o = super(MyTestRunner, self).setup_databases()
        init_database()
        return o