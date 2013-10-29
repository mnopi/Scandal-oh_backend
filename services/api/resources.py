# -*- coding: utf-8 -*-
import glob
import json
import re
import urlparse
from django.conf.urls import url
from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import simplejson
from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from tastypie.resources import ModelResource
from services.api.resource_authorization import ResourceAuthorization
from services.models import *
from services.utils import *
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

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/login/$" % (self._meta.resource_name),
                self.wrap_view('login_user'),
                name="api_login_user"),
        ]

    def login_user(self, request, **kwargs):
        if request.method == 'POST':
            posted_data = simplejson.loads(request.body)
            username = email = posted_data[0]
            password = posted_data[1]
            user = authenticate(username=username, password=password)
            if user is None:
                # si falla con el nombre de usuario se comprueba con el email
                username = CustomUser.objects.get(email=email).username
                user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return self.get_detail(request)
            else:
                resp = {
                    'status': 'error',
                    'reason': 'invalid login data',
                }
                return HttpResponse(simplejson.dumps(resp), mimetype="application/json")


class PhotoResource(MultipartResource, ModelResource):
    user = fields.ToOneField(CustomUserResource, 'user')
    category = fields.ToOneField('services.api.resources.CategoryResource', 'category')

    class Meta:
        resource_name = 'photo'
        queryset = Photo.objects.all().order_by('-date')
        authorization = ResourceAuthorization('user')
        always_return_data = True
        filtering = {
            'user': ALL_WITH_RELATIONS,
            'category': ALL_WITH_RELATIONS,
            'id': ALL
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
        img_original = bundle.obj.img.file.name
        # img_path_resized = bundle.obj.get_img_thumbnail_path()
        ImgResizer().resize(img_original)
        #
        # subimos al bucket, eliminando los locales
        S3BucketHandler().push_file(img_original, bundle.obj.img.name)
        # b.push_file(img_path_resized, bundle.obj.get_img_thumbnail_name())
        return obj

    def dehydrate(self, bundle):
        bundle.data['comments_count'] = Comment.objects.filter(photo=bundle.obj).count()
        return bundle


class CategoryResource(ModelResource):
    class Meta:
        resource_name = 'category'
        queryset = Category.objects.all()
        authorization = ResourceAuthorization('user')
        always_return_data = True
        filtering = {
            'id': ALL,
        }


class CommentResource(ModelResource):
    user = fields.ToOneField(CustomUserResource, 'user')
    photo = fields.ToOneField(PhotoResource, 'photo')
    class Meta:
        resource_name = 'comment'
        queryset = Comment.objects.all()
        authorization = ResourceAuthorization('user')
        always_return_data = True
        filtering = {
            'user': ALL_WITH_RELATIONS,
            'photo': ALL_WITH_RELATIONS,
            'id': ALL,
        }

    def dehydrate(self, bundle):
        bundle.data['username'] = bundle.obj.user.username
        bundle.data['user_id'] = bundle.obj.user.id
        return bundle