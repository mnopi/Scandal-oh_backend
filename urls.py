from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from tastypie.api import Api
from services.api.resources import *

from settings.common import MEDIA_ROOT

v1_api = Api()
v1_api.register(CustomUserResource())
v1_api.register(PhotoResource())
v1_api.register(CategoryResource())
v1_api.register(CommentResource())


urlpatterns = patterns('',
    url(r'^api/', include(v1_api.urls)),
    url(r'^services/', include('services.urls')),
    url(r'^test/', include('tests.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': MEDIA_ROOT}),
)
