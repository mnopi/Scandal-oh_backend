# -*- coding: utf-8 -*-

from pydub import AudioSegment
import os
import subprocess
from services.utils import rename_extension, change_directory, get_extension
from settings import common
from tests.utils import TEST_SOUNDS_COPIES_PATH


class AudioHelper:
    DEFAULT_CONVERSION_FORMAT = '3gp'

    @classmethod
    def convert(cls, file_from, file_to=None, fmt=None):
        fmt = fmt or cls.DEFAULT_CONVERSION_FORMAT
        file_from_fmt = get_extension(file_from)
        if file_from_fmt != fmt:
            file_to = file_to or rename_extension(file_from, fmt)
            if common.UNIT_TEST_MODE:
                file_to = change_directory(file_to, TEST_SOUNDS_COPIES_PATH)

            params1 = params2 = []
            if fmt == '3gp':
                params1.extend([
                    '-ar', '8000',
                    '-ac', '1',
                ])

            # construimos el cmd a invocar
            cmd = [
                AudioSegment.ffmpeg,
                '-i',
                file_from,
            ]
            cmd.extend(params1)
            cmd.append(file_to)
            cmd.extend(params2)

            # ffmpeg -i European\ Siren.caf -ar 8000 -ac 1 test_copies/to.3gp
            subprocess.call(cmd,
                            # make ffmpeg shut up
                            stderr=open(os.devnull)
            )
            return file_to
        else:
            return file_from