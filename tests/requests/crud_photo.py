# # -*- coding: utf-8 -*-
from django.test import TestCase
import simplejson
from services.models import *
from services.utils import S3BucketHandler
from settings.test import MEDIA_TEST
from tests.factories import *

from tests.runner import SplinterTestCase
from tests.utils import client, API_BASE_URI, TEST_IMGS_PATH, get_file_from_bucket, content_type_ok_ext
from django.test import client as f_client


class CrudPhotoTest(TestCase):
    def test_create_photo(self):
        # GIVEN
        #   un usuario y una categoría
        CustomUserFactory()
        CategoryFactory()
        # WHEN
        #   envío la foto al servidor
        with open(os.path.join(TEST_IMGS_PATH, 'test_img_portrait.png')) as img:
            data = {
                "user": "/api/v1/user/1/",
                "category": "/api/v1/category/1/",
                "title": "This is a title bla bla bla",
                "img": img
            }
            resp = client.post(API_BASE_URI + 'photo/', data=data)
        # THEN
        #   respuesta ok y que se haya creado en BD la foto
        assert resp.status_code == 201
        new_photo = Photo.objects.all()[0]
        assert new_photo.id is not None
        #   AND que el archivo se haya subido correctamente al bucket
        resp = get_file_from_bucket(new_photo.img.name)
        assert content_type_ok_ext(resp, 'image/')
        #   AND que el archivo en servidor local esté eliminado
        path = os.path.join(MEDIA_TEST, 'photos',
                            'cat_' + str(new_photo.category.id),
                            'photo_' + str(new_photo.id) + '.png')
        assert not os.path.exists(path)
        #   AND quitamos del bucket la imagen subida de prueba
        S3BucketHandler().remove_file(new_photo.img.name)
        try:
            get_file_from_bucket(new_photo.img.name)
        except Exception:
            assert True
        else:
            assert False

    def test_read_photo_list(self):
        # given
        PhotoFactory.create_batch(2)
        # when
        resp = client.get(API_BASE_URI + 'photo/')
        # then
        assert resp.status_code == 200
        assert len(simplejson.loads(resp.content)['objects']) == 2

    # def test_read_photo(self):
    #     # given
    #     PhotoFactory()
    #     # when
    #     resp = client.get(API_BASE_URI + 'photo/1/')
    #     # then
    #     assert resp.status_code == 200
    #     assert simplejson.loads(resp.content)['resource_uri'] is not None
    #
    # def test_update_photo(self):
    #     # given
    #     CommentFactory(text='comment original blahblah')
    #     # when
    #     text_edited = 'comment edited!!'
    #     resp = client.put(API_BASE_URI + 'comment/1/', data={'text': text_edited})
    #     # then
    #     assert resp.status_code == 200
    #     assert simplejson.loads(resp.content)['text'] == text_edited
    #
    # def test_delete_photo(self):
    #     # given
    #     CommentFactory()
    #     # when
    #     resp = client.delete(API_BASE_URI + 'comment/1/')
    #     # then
    #     assert resp.status_code == 204
    #     assert Comment.objects.all().count() == 0
    #
