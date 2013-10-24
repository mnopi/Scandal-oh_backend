# -*- coding: utf-8 -*-
import glob
import json
import urlparse
from django.http import HttpResponse
import simplejson
from tastypie import fields
from tastypie.authorization import DjangoAuthorization

from tastypie.resources import ModelResource
from services.api.resource_authorization import ResourceAuthorization
from services.models import *
from services.utils import tx_json_to_multipart
from settings.common import MEDIA_ROOT


class MultipartResource(object):
    def deserialize(self, request, data, format=None):
        if not format:
            format = request.META.get('CONTENT_TYPE', 'application/json')
        if format == 'application/x-www-form-urlencoded':
            return request.POST
        if format.startswith('multipart'):
            data = request.POST.copy()
            data.update(request.FILES)
            return data
        return super(MultipartResource, self).deserialize(request, data, format)


class CustomUserResource(ModelResource):
    class Meta:
        resource_name = 'user'
        queryset = CustomUser.objects.all()
        authorization = ResourceAuthorization('user')
        max_limit = 5000
        always_return_data = True
        # filtering = {
        #     'id': ALL,
        #     'username': ALL,
        #     }


class PhotoResource(MultipartResource, ModelResource):
    user = fields.ToOneField(CustomUserResource, 'user')
    category = fields.ToOneField('services.api.resources.CategoryResource', 'category')

    class Meta:
        resource_name = 'photo'
        queryset = Photo.objects.all()
        authorization = ResourceAuthorization('user')
        max_limit = 5000
        always_return_data = True
        filtering = {
            'user'
        }
        ordering = {
            'date'
        }

    def obj_create(self, bundle, **kwargs):
        # dependiendo si la petición llega en formato json puro..
        if bundle.request.META['CONTENT_TYPE'] == 'application/json':
            bundle.data = tx_json_to_multipart(bundle.request.body)
        super(type(self), self).obj_create(bundle)
        # en /media/ borra todos los archivos que comienzen por delete_me
        for filename in glob.glob(os.path.join(MEDIA_ROOT, 'delete_me*')):
            os.remove(filename)
        return self.obj_update(bundle)

    # def obj_update(self, bundle, skip_errors=False, **kwargs):
    #     return HttpResponse(simplejson.dumps(bundle.data), mimetype='application/json')


class CategoryResource(ModelResource):
    class Meta:
        resource_name = 'category'
        queryset = Category.objects.all()
        authorization = ResourceAuthorization('user')


class CommentResource(ModelResource):
    class Meta:
        resource_name = 'comment'
        queryset = Comment.objects.all()
        authorization = ResourceAuthorization('user')
