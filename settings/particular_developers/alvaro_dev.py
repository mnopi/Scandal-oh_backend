from settings.common import *
from settings.dev import *


ALLOWED_HOSTS = ['*']
DEBUG = True

#Alfredo's local database
#
DATABASES = {
    "default": {
    "ENGINE": "django.db.backends.mysql",
    "NAME": "labelee_eventos",
    "USER": "mnopi",
    "PASSWORD": "1aragon1",
    "HOST": "192.168.1.120",
    "PORT": "",
    }
}
