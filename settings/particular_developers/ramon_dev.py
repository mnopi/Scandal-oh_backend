from settings.common import *
from settings.dev import *


#
# PYDUB
import pydub
pydub.AudioSegment.ffmpeg = "/usr/local/bin/ffmpeg"
