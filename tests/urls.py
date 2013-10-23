from django.conf.urls import patterns, url


urlpatterns = patterns(
    'tests.views',

    url(r'^photo/$', 'create_photo', name='create_photo'),
    # url(r'^$', 'create_photo', name='create_photo'),
)