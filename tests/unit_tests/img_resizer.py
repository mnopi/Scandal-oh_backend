# -*- coding: utf-8 -*-
import os
from shutil import copyfile
from PIL import Image
from django.test import TestCase
from settings.common import PROJECT_ROOT
from services.utils import ImgResizer


class ImgResizerTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.img_original_landscape = os.path.join(PROJECT_ROOT, '../', 'fixtures', 'imgs', 'test_img_landscape.png')
        cls.img_original_portrait = os.path.join(PROJECT_ROOT, '../', 'fixtures', 'imgs', 'test_img_portrait.png')
        cls.img_original_copy = os.path.join(PROJECT_ROOT, '../', 'fixtures', 'imgs', 'test_img_copy.png')
        cls.img_resized = os.path.join(PROJECT_ROOT, '../', 'fixtures', 'imgs', 'resized.png')

    def tearDown(self):
        if os.path.exists(self.img_resized):
            os.remove(self.img_resized)
        if os.path.exists(self.img_original_copy):
            os.remove(self.img_original_copy)

    def test_resize_landscape_img_to_given_width(self):
        ImgResizer().resize(self.img_original_landscape, self.img_resized, fixed_width=250)
        assert os.path.exists(self.img_resized)
        img = Image.open(self.img_resized)
        assert img.size[0] == 250

    def test_resize_portrait_img_to_given_height(self):
        ImgResizer().resize(self.img_original_portrait, self.img_resized, fixed_height=500)
        assert os.path.exists(self.img_resized)
        img = Image.open(self.img_resized)
        assert img.size[1] == 500

    def test_resize_img_overwriting_original(self):
        img_original = os.path.join(PROJECT_ROOT, '../', 'fixtures', 'imgs', 'test_img.png')
        copyfile(img_original, self.img_original_copy)
        ImgResizer().resize(self.img_original_copy, fixed_height=500)
        assert os.path.exists(self.img_original_copy)
        img = Image.open(self.img_original_copy)
        assert img.size[1] == 500

