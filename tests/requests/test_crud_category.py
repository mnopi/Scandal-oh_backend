# # -*- coding: utf-8 -*-
from django.test import TestCase
import simplejson
from services.models import *
from settings.common import API_BASE_URI
from tests.factories import *

from tests.utils import client


class CrudCategoryTest(TestCase):
    def test_create_category(self):
        # given
        # when
        new_category_name = 'smiling'
        data = simplejson.dumps({"name": new_category_name})
        resp = client.post(API_BASE_URI + 'category/', data=data, content_type='application/json')
        # then
        assert resp.status_code == 201
        assert simplejson.loads(resp.content)['name'] == new_category_name
        new_category = Category.objects.all().order_by('id').reverse()[0]
        assert new_category.name == new_category_name
        assert new_category.id is not None

    def test_read_category_list(self):
        # given
        CategoryFactory.create_batch(2)
        # when
        resp = client.get(API_BASE_URI + 'category/')
        # then
        assert resp.status_code == 200
        assert len(simplejson.loads(resp.content)['objects']) == 2

    def test_read_category(self):
        # given
        CategoryFactory()
        # when
        resp = client.get(API_BASE_URI + 'category/1/')
        # then
        assert resp.status_code == 200
        assert simplejson.loads(resp.content)['name'] is not None

    def test_update_category(self):
        # given
        CategoryFactory(name='original name')
        # when
        name_edited = 'edited naaaaññmeóóé'
        data = simplejson.dumps({'name': name_edited})
        resp = client.put(API_BASE_URI + 'category/1/', data=data, content_type='application/json')
        # then
        assert resp.status_code == 200
        assert simplejson.loads(resp.content)['name'] == name_edited.decode('utf-8')

    def test_delete_category(self):
        # given
        CommentFactory()
        # when
        resp = client.delete(API_BASE_URI + 'category/1/')
        # then
        assert resp.status_code == 204
        assert Category.objects.all().count() == 0

