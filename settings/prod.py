"""Production settings and globals."""

from common import *

# Production secret
#########################################
SECRET_KEY = os.environ['SECRET_KEY']

# Production database
#########################################
DATABASES = {
    "default": {
    "ENGINE": "django.db.backends.mysql",
    "NAME": "labelee",
    "USER": "root",
    "PASSWORD": os.environ['DB_PASSWORD'],
    "HOST": "",
    "PORT": "",
    }
}
##########################################

# DEBUG MODE IS OFF!!
####################################
DEBUG = False
TEMPLATE_DEBUG = DEBUG
####################################


# Only allowed hosts!!
####################################
ALLOWED_HOSTS = ['localhost:8000', '127.0.0.1', '192.168.1.33', '.compute.amazonaws.com', '.compute-1.amazonaws.com']   #TODO: dejar el que toque!
####################################


# YahooId  : labelee_server@yahoo.com
# Password : 1Aragon1
ADMINS = (
    ('Labeloncio', 'labelee_server@yahoo.com'),
)

MANAGERS = ADMINS