from settings.common import *
from settings.dev import *
# from settings.test import *


#
# PYDUB
import pydub
pydub.AudioSegment.ffmpeg = "/usr/local/bin/ffmpeg"
