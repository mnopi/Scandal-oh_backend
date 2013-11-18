# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
import simplejson
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from tastypie.resources import ModelResource
from tastypie.validation import FormValidation
from logger import Logger
from services.api.resource_authorization import ResourceAuthorization
from services.audio_helper import AudioHelper
from services.forms import CustomUserRegisterForm, CustomUserLoginForm, CustomUserUpdateForm
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

    def error_response(self, request, errors, response_class=None):
        full_errors = {
            'status': 'error',
            'reason': errors['user']
        }
        return super(CustomUserResource, self).error_response(request, full_errors, response_class=HttpResponse)

    def obj_create(self, bundle, **kwargs):
        "Para el registro de usuario"
        self._meta.validation = FormValidation(form_class=CustomUserRegisterForm)
        if 'social_network' in bundle.data:
            bundle.data['password'] = '123456'
        bundle_created = super(CustomUserResource, self).obj_create(bundle, **kwargs)
        resp = self.full_dehydrate(bundle_created)
        resp.data['status'] = 'ok'
        return resp

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        self._meta.validation = FormValidation(form_class=CustomUserUpdateForm)
        return super(CustomUserResource, self).obj_update(bundle, **kwargs)

    def get_dehydrated_user(self, user_obj, request):
        """
        obtiene el usuario en formato tastypie
        """
        r = CustomUserResource()
        bundle = r.build_bundle(obj=user_obj, request=request)
        return r.full_dehydrate(bundle).data

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/login/$" % (self._meta.resource_name),
                self.wrap_view('login_user'),
                name="api_login_user"
            ),
        ]

    def login_user(self, request, **kwargs):
        if request.method == 'POST':
            posted_data = simplejson.loads(request.body)
            if 'social_network' in posted_data:
                username = posted_data['username']
                email = posted_data['email']
                user = authenticate(username=username, from_social_network=True)
                # si no aparece como registrado desde facebook se crea
                if not user:
                    user = CustomUser.objects.create(
                        username=username,
                        email=email,
                        password='123456',
                        social_network=1
                    )
            else:
                username = email = posted_data['username_email']
                password = posted_data['password']
                user = authenticate(username=username, password=password)
            resp_error = {'status': 'error',}
            resp_ok = {'status': 'ok',}
            resp = None
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
                            resp_ok['user_uri'] = self.get_dehydrated_user(user, request)['resource_uri']
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
            if not 'social_network' in posted_data:
                form = CustomUserLoginForm({
                    'username_email': posted_data['username_email'],
                    'password': posted_data['password']
                })
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
            'id': ALL,
            'country': ALL,
        }
        ordering = {
            'date'
        }

    def obj_create(self, bundle, **kwargs):
        try:
            img = bundle.data['img']
            del bundle.data['img']
            sound = None
            if 'sound' in bundle.data:
                sound = bundle.data['sound']
                del bundle.data['sound']
            super(type(self), self).obj_create(bundle)
            bundle.data['img'] = img
            if sound:
                bundle.data['sound'] = sound
            return self.obj_update(bundle)
        except Exception as ex:
            Logger.error(str(ex))

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        obj = super(type(self), self).obj_update(bundle)
        # subimos las imagenes al bucket
        if 'img' in bundle.data:
            img_original = bundle.obj.img.path
            # comprimimos la imagen original y creamos la copia redimensionada
            img_resized = ImgHelper().resize(img_original)
            # subimos archivos al bucket, eliminando los locales
            S3BucketHandler.push_file(img_original, bundle.obj.img.name)
            S3BucketHandler.push_file(img_resized, bundle.obj.get_img_p_name())
        # subimos el audio convertido al bucket
        if 'sound' in bundle.data:
            # convertimos audio
            audio_converted = AudioHelper.convert(bundle.obj.sound.path, delete_original=True)
            # cambiamos la extensión del archivo al que apunta el objeto photo en BD
            ext = get_extension(audio_converted)
            file_id = rename_extension(bundle.obj.sound.name, ext)
            bundle.obj.sound.name = file_id
            bundle.obj.save()
            S3BucketHandler.push_file(audio_converted, file_id)
        # todo: si se edita una foto que tenía sonido a sin sonido, entonces eliminarlo
        # del bucket
        return obj

    def obj_delete(self, bundle, **kwargs):
        super(type(self), self).obj_delete(bundle)

    def dehydrate(self, bundle):
        bundle.data['comments_count'] = Comment.objects.filter(photo=bundle.obj).count()
        bundle.data['latitude'] = -1 if bundle.data['latitude'] == 0 else bundle.data['latitude']
        bundle.data['longitude'] = -1 if bundle.data['longitude'] == 0 else bundle.data['longitude']
        bundle.data['img_p'] = bundle.obj.get_img_p_name()
        return bundle

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/(?P<country>[A-Z]{2})/previous/$"
                % (self._meta.resource_name),
                self.wrap_view('get_prev_photos'),
                name="api_get_prev_photos"
            ),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/(?P<country>[A-Z]{2})/new/$"
                % (self._meta.resource_name),
                self.wrap_view('get_new_photos'),
                name="api_get_new_photos"
            ),
        ]

    def get_prev_photos(self, request, **kwargs):
        "Muestra las 10 fotos previas a una dada, todas también con el país dado"
        p = Photo.objects.get(pk=kwargs['pk'])
        photos = Photo.objects.filter(
            country=kwargs['country'],
            date__lt=p.date
        ).order_by('-date')[:10]
        bundles = []
        for p in photos:
            bundle = self.build_bundle(obj=p, request=request)
            bundles.append(self.full_dehydrate(bundle, for_list=True))
        list_json = self.serialize(None, bundles, "application/json")
        return HttpResponse(list_json, mimetype="application/json")

    def get_new_photos(self, request, **kwargs):
        "Muestra todas las fotos de un país dado, a partir de la foto dada"
        p = Photo.objects.get(pk=kwargs['pk'])
        photos = Photo.objects.filter(
            country=kwargs['country'],
            date__gt=p.date
        ).order_by('-date')
        bundles = []
        for p in photos:
            bundle = self.build_bundle(obj=p, request=request)
            bundles.append(self.full_dehydrate(bundle, for_list=True))
        list_json = self.serialize(None, bundles, "application/json")
        return HttpResponse(list_json, mimetype="application/json")



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