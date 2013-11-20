# -*- coding: utf-8 -*-
import os
from services.audio_helper import AudioHelper
from settings.common import TEST_SOUNDS_PATH, TEST_SOUNDS_COPIES_PATH
from tests.testcase_classes import UnitTestCase
from tests.utils import *


class AudioConverterTest(UnitTestCase):
    @classmethod
    def setUpClass(cls):
        super(AudioConverterTest, cls).setUpClass()
        cls.audio_original_caf = os.path.join(TEST_SOUNDS_PATH, 'prueba de sonido.caf')
        cls.audio_original_3gp = os.path.join(TEST_SOUNDS_PATH, 'prueba de sonido.3gp')
        reset_folder(TEST_SOUNDS_COPIES_PATH)

    def tearDown(self):
        reset_folder(TEST_SOUNDS_COPIES_PATH)

    def __assert_conversion_ok__(self, file_from, fmt):
        audio_converted = AudioHelper.convert(file_from, fmt=fmt)
        assert os.path.isfile(audio_converted)
        assert audio_converted != file_from

    def __assert_conversion_failed__(self, file_from, fmt):
        audio_converted = AudioHelper.convert(file_from, fmt=fmt)
        assert not os.path.isfile(audio_converted)
        assert audio_converted != file_from

    def __assert_same_format__(self, file_from, fmt):
        audio_converted = AudioHelper.convert(file_from, fmt=fmt)
        assert os.path.isfile(audio_converted)
        assert audio_converted == file_from

    # desde caf

    def test_convert_caf_to_3gp(self):
        self.__assert_conversion_ok__(self.audio_original_caf, '3gp')

    def test_convert_caf_to_mp3(self):
        self.__assert_conversion_ok__(self.audio_original_caf, 'mp3')

    # desde 3gp

    def test_convert_3gp_to_3gp(self):
        self.__assert_same_format__(self.audio_original_3gp, '3gp')

    def test_convert_3gp_to_mp3(self):
        self.__assert_conversion_ok__(self.audio_original_3gp, 'mp3')

