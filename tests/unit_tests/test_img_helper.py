# -*- coding: utf-8 -*-
import os
from shutil import copyfile
from PIL import Image
from services.utils import ImgHelper
from settings.common import TEST_IMGS_PATH, TEST_IMGS_COPIES_PATH
from tests.testcase_classes import UnitTestCase
from tests.utils import reset_folder


class ImgResizerTest(UnitTestCase):
    @classmethod
    def setUpClass(cls):
        super(ImgResizerTest, cls).setUpClass()
        cls.img_original_landscape = os.path.join(TEST_IMGS_PATH, 'test_img_landscape.png')
        cls.img_original_portrait = os.path.join(TEST_IMGS_PATH, 'test_img_portrait.png')
        cls.img_original_copy = os.path.join(TEST_IMGS_COPIES_PATH, 'img_original.png')
        cls.i = ImgHelper()
        reset_folder(TEST_IMGS_COPIES_PATH)

    def tearDown(self):
        reset_folder(TEST_IMGS_COPIES_PATH)

    def __assert_resized_to__(self, img_file, fixed_width=None, fixed_height=None):
        copyfile(img_file, self.img_original_copy)
        if fixed_width:
            self.i.resize(self.img_original_copy, fixed_width=fixed_width)
            img = Image.open(self.i.img_resized_path)
            assert img.size[0] == fixed_width
        elif fixed_height:
            self.i.resize(self.img_original_copy, fixed_height=fixed_height)
            img = Image.open(self.i.img_resized_path)
            assert img.size[1] == fixed_height
        else:
            self.i.resize(self.img_original_copy)
            img = Image.open(self.i.img_resized_path)
            assert img.size[1] == 640 or img.size[1] == 480
        assert os.path.exists(self.i.img_compressed_path)
        assert os.path.exists(self.i.img_resized_path)
        assert not os.path.exists(self.i.img_from_path)

    def test_resize_img(self):
        self.__assert_resized_to__(self.img_original_portrait)

    def test_resize_landscape_img_to_given_width(self):
        self.__assert_resized_to__(self.img_original_landscape, fixed_width=250)

    def test_resize_portrait_img_to_given_height(self):
        self.__assert_resized_to__(self.img_original_portrait, fixed_height=500)
