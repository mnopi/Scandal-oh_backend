# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms import ModelForm, CharField, Form, EmailField
from django.utils.translation import gettext as _
from services.models import CustomUser

def validate_email_unique(value):
    value = value.encode('utf-8')
    exists = CustomUser.objects.filter(email=value)
    if exists:
        raise ValidationError(_('Esta dirección email ya existe como registrada') + ': %s' % value)

validate_alphanumeric_username = RegexValidator(r'^[0-9a-zA-Z_]*$', _('Sólo están permitidos caracteres alfanuméricos'))
validate_alphanumeric_email = RegexValidator(r'^[0-9a-zA-Z@\._]*$', _('Sólo están permitidos caracteres alfanuméricos (excepto @ y . para el email)'))


class CustomUserRegisterForm(ModelForm):
    username = CharField(required=True, min_length=4, max_length=30, validators=[validate_alphanumeric_username])
    email = CharField(required=True, validators=[validate_alphanumeric_email, validate_email_unique])
    password = CharField(required=True, min_length=6, max_length=128)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password',]


class CustomUserLoginForm(Form):
    username_email = CharField(required=True, min_length=4, validators=[validate_alphanumeric_email])
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
