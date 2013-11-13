from settings.common import *
# from settings.dev import *

DEBUG = True
TEST_MODE = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['localhost:8000', '127.0.0.1', '192.168.1.129', '.compute.amazonaws.com', '.compute-1.amazonaws.com']   #TODO: dejar el que toque!


#Ramon's local database
#
# DATABASES = {
#     "default": {
#     "ENGINE": "django.db.backends.mysql",
#     "NAME": "scandaloh_test",
#     "USER": "root",
#     "PASSWORD": "",
#     "HOST": "",
#     "PORT": "",
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "scandaloh_dev",
        "USER": "mnopi",
        "PASSWORD": "1aragon1",
        "HOST": "192.168.1.201",
        "PORT": "",
    }
}

#
# PYDUB
import pydub
pydub.AudioSegment.ffmpeg = "/usr/local/bin/ffmpeg"
