"""Development settings and globals."""

from common import *

import common
common.DEV_MODE = True

#     Estas aplicaciones solo se usaran en desarrollo..
INSTALLED_APPS += ('south',)


## DEBUG =
## TEMPLATE_DEBUG = DEBUG