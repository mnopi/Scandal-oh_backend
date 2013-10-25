# -*- coding: utf-8 -*-
import glob
import json
import re
import urlparse
from django.http import HttpResponse
import simplejson
from tastypie import fields
from tastypie.authorization import DjangoAuthorization

from tastypie.resources import ModelResource
from services.api.resource_authorization import ResourceAuthorization
from services.models import *
from services.utils import tx_json_to_multipart, delete_files, resize_img_width, S3BucketHandler
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
        queryset = Photo.objects.all().order_by('-date')
        authorization = ResourceAuthorization('user')
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
        delete_files(os.path.join(MEDIA_ROOT, 'delete_me*'))
        return self.obj_update(bundle)

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        obj = super(type(self), self).obj_update(bundle)
        img_path_original = bundle.obj.img.file.name
        img_path_resized = bundle.obj.get_img_thumbnail_path()
        resize_img_width(img_path_original, img_path_resized, 300)
        #
        # subimos al bucket, eliminando los locales
        print 'uploading files to bucket..'
        b = S3BucketHandler()
        b.push_file(img_path_original, bundle.obj.img.name)
        b.push_file(img_path_resized, bundle.obj.get_img_thumbnail_name())
        return obj

    def dehydrate(self, bundle):
        bundle.data['comments_count'] = Comment.objects.filter(photo=bundle.obj).count()
        return bundle


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
