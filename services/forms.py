# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms import ModelForm, CharField, Form, EmailField
from django.utils.translation import gettext as _
from services.models import *


def validate_email_unique(value):
    value = value.encode('utf-8')
    exists = CustomUser.objects.filter(email=value)
    if exists:
        raise ValidationError(_('Esta dirección email ya existe como registrada') + ': %s' % value)

validate_alphanumeric_username = RegexValidator(r'^[0-9a-zA-Z_]*$', _('Sólo están permitidos caracteres alfanuméricos'))
validate_alphanumeric_email = RegexValidator(r'^[0-9a-zA-Z@\._]*$', _('Sólo están permitidos caracteres alfanuméricos (excepto @ y .)'))

username_max_length = 25

class CustomUserRegisterForm(ModelForm):
    username = CharField(required=True, min_length=4, max_length=username_max_length,
                         validators=[validate_alphanumeric_username],
                         error_messages={'unique': _('Ya existe un usuario con este nombre')})
    email = CharField(required=True, validators=[validate_alphanumeric_email, validate_email_unique])
    password = CharField(required=True, min_length=6, max_length=128)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password',]


class CustomUserUpdateForm(ModelForm):
    username = CharField(required=False, min_length=4, max_length=username_max_length,
                         validators=[validate_alphanumeric_username],
                         error_messages={'unique': _('Ya existe un usuario con este nombre')})
    email = CharField(required=False, validators=[validate_alphanumeric_email])
    password = CharField(required=False, min_length=6, max_length=128)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password',]


class CustomUserLoginForm(ModelForm):
    username_email = CharField(required=True, min_length=4, validators=[validate_alphanumeric_email])

    class Meta:
        model = CustomUser
        fields = ['password',]

    # def full_clean(self):
    #     super(CustomUserLoginForm, self).full_clean()
    #     if self.cleaned_data.get('film') and 'director' in self._errors:
    #         del self._errors['director']


    # def clean_username(self):
    #     username = self.cleaned_data.get('username')
    #     if username and CustomUser.objects.filter(username=username).count():
    #         pass
    #     return email

# customUserRegisterForm = FormValidation(form_class=CustomUserRegisterForm)

class PhotoForm(ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'country',]


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text',]
