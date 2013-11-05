# -*- coding: utf-8 -*-
import glob
import json
import re
import urlparse
from django.conf.urls import url
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import simplejson
from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from tastypie.resources import ModelResource
from tastypie.validation import FormValidation
from services.api.resource_authorization import ResourceAuthorization
from services.forms import CustomUserRegisterForm, CustomUserLoginForm
from services.models import *
from services.utils import *
from settings.common import MEDIA_ROOT
from tests.utils import reset_folder


class MultipartResource(object):
    "https://github.com/toastdriven/django-tastypie/issues/42#issuecomment-5485666"
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

class ErrorResponseMixin(object):
    def error_response(self, request, errors, response_class=None):
        full_errors = {
            'status': 'error',
            'reason': errors
        }
        return super(ErrorResponseMixin, self).error_response(request, full_errors, response_class=HttpResponse)



class CustomUserResource(ErrorResponseMixin, ModelResource):
    class Meta:
        resource_name = 'user'
        queryset = CustomUser.objects.all()
        authorization = ResourceAuthorization('user')
        always_return_data = True
        validation = FormValidation(form_class=CustomUserRegisterForm)
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

    def get_dehydrated_user(self, user_obj, request):
        """
        obtiene el usuario en formato tastypie
        """
        r = CustomUserResource()
        bundle = r.build_bundle(obj=user_obj, request=request)
        return r.full_dehydrate(bundle).data

    def login_user(self, request, **kwargs):
        if request.method == 'POST':
            posted_data = simplejson.loads(request.body)
            username = email = posted_data['username_email']
            password = posted_data['password']
            resp_error = {'status': 'error',}
            resp_ok = {'status': 'ok',}
            resp = None
            user = authenticate(username=username, password=password)
            if user is None:
                # si falla con el nombre de usuario se comprueba con el email
                users_with_that_username = CustomUser.objects.filter(username=username)
                users_with_that_email = CustomUser.objects.filter(email=email)
                if users_with_that_username:
                    resp_error['reason'] = 'invalid password'
                    resp_error['reason_code'] = 2
                    resp = resp_error
                elif not users_with_that_email:
                    resp_error['reason'] = 'invalid username/email'
                    resp_error['reason_code'] = 1
                    resp = resp_error
                else:
                    # si hay usuario con ese email..
                    username = users_with_that_email[0].username
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        if user.is_active:
                            login(request, user)
                            resp_ok['user_uri'] = user.id
                            resp = resp_ok
                    else:
                        # email ok pero password no
                        resp_error['reason'] = 'invalid password'
                        resp_error['reason_code'] = 2
                        resp = resp_error
            else:
                # si hay usuario con ese username, entonces el login es correcto
                resp_ok['user_uri'] = self.get_dehydrated_user(user, request)['resource_uri']
                resp = resp_ok

            # si no están bien los campos del formulario devolverá un error
            form = CustomUserLoginForm({'username_email': posted_data['username_email'], 'password': posted_data['password']})
            if not form.is_valid():
                resp_error['reason'] = 'invalid form data'
                resp_error['reason_details'] = form.errors
                resp_error['reason_code'] = 3
                resp = resp_error

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
        # # dependiendo si la petición llega en formato json puro..
        # if bundle.request.META['CONTENT_TYPE'] == 'application/json':
        #     bundle.data = tx_json_to_multipart(bundle.request.body)
        super(type(self), self).obj_create(bundle)
        # en /media/ borra todos los archivos que comienzen por delete_me
        delete_files(os.path.join(MEDIA_ROOT, 'delete_me*'))
        return self.obj_update(bundle)

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        obj = super(type(self), self).obj_update(bundle)
        img_original = bundle.obj.img.path
        # comprimimos la imagen original y creamos la copia redimensionada
        ImgHelper().resize(img_original)
        # subimos archivos al bucket, eliminando los locales
        S3BucketHandler.push_file(img_original, bundle.obj.img.name)
        S3BucketHandler.push_file(bundle.obj.get_img_p_path(), bundle.obj.get_img_p_name())
        S3BucketHandler.push_file(bundle.obj.sound.path, bundle.obj.sound.name)
        # nos aseguramos que dejamos /media limpia
        reset_folder(MEDIA_ROOT)
        return obj

    def obj_delete(self, bundle, **kwargs):
        super(type(self), self).obj_delete(bundle)
        # eliminamos del bucket los archivos para la foto
        S3BucketHandler.remove_file(bundle.obj.img.name)
        S3BucketHandler.remove_file(bundle.obj.get_img_p_name())
        S3BucketHandler.remove_file(bundle.obj.sound.name)

    def dehydrate(self, bundle):
        bundle.data['comments_count'] = Comment.objects.filter(photo=bundle.obj).count()
        bundle.data['latitude'] = -1 if bundle.data['latitude'] == 0 else bundle.data['latitude']
        bundle.data['longitude'] = -1 if bundle.data['longitude'] == 0 else bundle.data['longitude']
        bundle.data['img_p'] = bundle.obj.get_img_p_name()
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
        queryset = Comment.objects.all().order_by('-date')
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