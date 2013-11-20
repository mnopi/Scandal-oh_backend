from django_nose import NoseTestSuiteRunner
from tests.utils import reset_media_test_folder, client


# class MyTestRunner(DjangoTestSuiteRunner):
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