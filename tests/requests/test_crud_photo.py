# # -*- coding: utf-8 -*-
import shutil
from django.test import TestCase
import simplejson
from services.models import *
from services.utils import S3BucketHandler
from settings.test import MEDIA_TEST
from tests.factories import *

from tests.runner import SplinterTestCase
from tests.utils import client, API_BASE_URI, TEST_IMGS_PATH, get_file_from_bucket, content_type_ok_ext, reset_media_test_folder, check_from_bucket, TEST_SOUNDS_PATH


def create_photo():
    # GIVEN
    #   un usuario y una categoría
    CustomUserFactory()
    CategoryFactory()
    # WHEN
    #   envío la foto al servidor
    with open(os.path.join(TEST_IMGS_PATH, 'test_img_portrait.jpg')) as img:
        with open(os.path.join(TEST_SOUNDS_PATH, 'European Siren.caf')) as sound:
            data = {
                "user": "/api/v1/user/1/",
                "category": "/api/v1/category/1/",
                "title": "This is a title bla bla bla",
                "img": img,
                "sound": sound
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
        file_list = [
            new_photo.img.name,
            new_photo.get_img_p_name(),
            new_photo.sound.name
        ]
        #   AND que los archivos se hayan subido correctamente al bucket
        check_from_bucket(file_list)
        #   AND que los archivos en servidor local estén eliminados
        path = os.path.join(MEDIA_TEST, 'photos',
                            'cat_' + str(new_photo.category.id),
                            'photo_' + str(new_photo.id))
        for file_extension in ['.png', '.jpg', '.caf']:
            assert not os.path.exists(path + file_extension)
            assert not os.path.exists(path + '.p' + file_extension)
        #   AND quitamos del bucket los archivos subidos de prueba
        S3BucketHandler.remove_file(new_photo.img.name)
        S3BucketHandler.remove_file(new_photo.get_img_p_name())
        S3BucketHandler.remove_file(new_photo.sound.name)
        check_from_bucket(file_list, check_removed=True)

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
        assert received_photos[1]['sound'] is not None
        assert received_photos[1]['img_p'] is not None

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
        photo_to_delete_dict = simplejson.loads(photo_to_delete.content)
        file_list = [
            photo_to_delete_dict['img'],
            photo_to_delete_dict['img_p'],
            photo_to_delete_dict['sound']
        ]
        check_from_bucket(file_list, check_removed=True)
