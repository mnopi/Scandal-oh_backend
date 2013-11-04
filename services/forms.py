# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms import ModelForm, CharField, Form, EmailField
from services.models import CustomUser

def validate_email_unique(value):
    exists = CustomUser.objects.filter(email=value)
    if exists:
        raise ValidationError(u'La dirección email %s ya existe como registrada' % value)

validate_alphanumeric = RegexValidator(r'^[0-9a-zA-Z@\._]*$', u'Sólo están permitidos caracteres alfanuméricos')


# def allow_duplicate_usernames(value):
#     exists = CustomUser.objects.filter(username=value)
#     if exists:
#         pass

class CustomUserRegisterForm(ModelForm):
    username = CharField(required=True, min_length=4, max_length=30)
    email = CharField(required=True, validators=[validate_email_unique])
    password = CharField(required=True, min_length=6, max_length=128)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password',]

class CustomUserLoginForm(Form):
    username_email = CharField(required=True, min_length=4, validators=[validate_alphanumeric])
    password = CharField(required=True, min_length=6, max_length=128)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password',]

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
