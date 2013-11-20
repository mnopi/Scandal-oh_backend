# -*- coding: utf-8 -*-
import os
import datetime

from django.contrib.auth.models import User, UserManager
from django.db import models
from services.utils import rename_to_p, S3BucketHandler, prepend_env_folder


class CustomUser(User):
    social_network = models.PositiveIntegerField(default=0, blank=True)

    class Meta:
        verbose_name = 'Custom user'
        verbose_name_plural = 'Custom users'

    objects = UserManager()

    def save(self, *args, **kwargs):
        # if self.social_network:
        #
        # else:
        # seteo la contraseña en BD a partir de la dada por el usuario
        if type(self) is CustomUser and not self.pk:
            self.set_password(self.password)
        super(CustomUser, self).save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True, blank=False)
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name


class Photo(models.Model):
    def get_photo_path(self, filename):
        if self.pk:
            fileName, fileExtension = os.path.splitext(filename)
            path = '%s/photos/cat_%s/photo_%s.jpg' % \
                   (self.country.upper(), self.category.id, self.id)
            return prepend_env_folder(path)

    def get_sound_path(self, filename):
        if self.pk:
            fileName, fileExtension = os.path.splitext(filename)
            path = '%s/photos/cat_%s/photo_%s_sound%s' % \
                   (self.country.upper(), self.category.id, self.id, fileExtension)
            return prepend_env_folder(path)

    user = models.ForeignKey(CustomUser, related_name='photos', blank=False)
    category = models.ForeignKey(Category, related_name='photos', blank=False, null=False)
    title = models.CharField(max_length=140, blank=False, null=False)
    img = models.FileField(upload_to=get_photo_path, null=True, blank=True)
    sound = models.FileField(upload_to=get_sound_path, null=True, blank=True)
    visits_count = models.PositiveIntegerField(default=0, blank=True)
    latitude = models.FloatField(null=True, blank=True, default=-1)
    longitude = models.FloatField(null=True, blank=True, default=-1)
    date = models.DateTimeField(default=datetime.datetime.utcnow())
    country = models.CharField(max_length=2, default='ES', null=False, blank=False)

    def __unicode__(self):
        return str(self.pk) + '_' + self.title

    # def save(self, *args, **kwargs):
    #     if self.date is None:
    #         self.date = datetime.datetime.now()
    #     super(Photo, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # if self.img:
        #     delete_file(self.img)
        # eliminamos del bucket los archivos para la foto
        S3BucketHandler.remove_file(self.img.name)
        S3BucketHandler.remove_file(self.get_img_p_name())
        if self.sound:
            S3BucketHandler.remove_file(self.sound.name)
        super(Photo, self).delete(*args, **kwargs)

    def get_img_p_name(self):
        return rename_to_p(self.img.name)

    def get_img_p_path(self):
        return rename_to_p(self.img.path)


class Comment(models.Model):
    user = models.ForeignKey(CustomUser, related_name='comments', blank=False)
    photo = models.ForeignKey(Photo, related_name='comments', blank=False)
    text = models.CharField(null=False, blank=False, max_length=500)
    date = models.DateTimeField(auto_now_add=True)


class LogEntry(models.Model):
    when = models.DateTimeField(auto_now=True)

    WARNING = 'WAR'
    DEBUG = 'DEB'
    INFO = 'INF'
    ERROR = 'ERR'
    CRITICAL = 'CRI'
    ENTRY_CATEGORY = {
        (WARNING, 'WAR'),
        (DEBUG, 'DEB'),
        (INFO, 'INF'),
        (ERROR, 'ERR'),
        (CRITICAL, 'CRI')
    }
    category = models.CharField(max_length=3, choices=ENTRY_CATEGORY, default=INFO)
    message = models.CharField(max_length=200, blank=True, null=True)

