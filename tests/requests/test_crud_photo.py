# # -*- coding: utf-8 -*-
import shutil
from django.test import TestCase
import simplejson
from services.models import *
from services.utils import S3BucketHandler
from settings.test import MEDIA_TEST
from tests.factories import *

from tests.runner import SplinterTestCase
from tests.utils import client, API_BASE_URI, TEST_IMGS_PATH, get_file_from_bucket, content_type_ok_ext, reset_media_test_folder

def create_photo():
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
        return client.post(API_BASE_URI + 'photo/', data=data)


class CrudPhotoTest(TestCase):
    def setUp(self):
        reset_media_test_folder()

    def test_create_photo(self):
        resp = create_photo()
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
        received_photos = simplejson.loads(resp.content)['objects']
        assert len(received_photos) == 2
        assert received_photos[0]['id'] is not None
        assert received_photos[1]['id'] is not None

    def test_read_photo(self):
        # given
        PhotoFactory()
        # when
        resp = client.get(API_BASE_URI + 'photo/1/')
        # then
        assert resp.status_code == 200
        assert simplejson.loads(resp.content)['resource_uri'] is not None

    def test_update_photo(self):
        # given
        PhotoFactory(title='original title')
        # when
        title_edited = 'edited title!!'
        data = simplejson.dumps({'title': title_edited})
        resp = client.put(API_BASE_URI + 'photo/1/', data=data, content_type="application/json")
        # then
        assert resp.status_code == 200
        assert simplejson.loads(resp.content)['title'] == title_edited

    def test_delete_photo(self):
        # given
        #   tenemos que tener una foto creada antes de poder eliminarla y así
        #   comprobar que también quedó borrada del bucket
        photo_to_delete = create_photo()
        # when
        resp = client.delete(API_BASE_URI + 'photo/1/')
        # then
        assert resp.status_code == 204
        assert Photo.objects.all().count() == 0
        try:
            get_file_from_bucket(photo_to_delete.img.name)
        except Exception:
            assert True
        else:
            assert False

# class GoogleTest(SplinterTestCase):
#     def test_search(self):
#         self.browser.visit('www.google.es')
#         pass

