###
#
# DJANGO-PIPELINE SETTINGS
#
###

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

# Para que funcione este compresor hay que instalar uglifyjs:
#   sudo npm install -g uglify-js
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.uglifyjs.UglifyJSCompressor'
PIPELINE_UGLIFYJS_ARGUMENTS = '-nm'
PIPELINE_DISABLE_WRAPPER = True

PIPELINE_CSS = {
    'map': {
        'source_filenames': (
            'vendor/leaflet/leaflet.css',
            'vendor/cubiq-add-to-homescreen-2.0.8/style/add2home.css',
            # 'css/map/index/leaflet.label.css',
            'css/map/index/social.network.menu.css',
            'css/map/index/animation.css',
            'css/map/index/idangerous.swiper.css',
            'css/map/index/helpmenu.css',
            'css/map/index/mmenu.css',
            'css/map/index/mmenu-positioning.css',
            'css/map/index/jqdialog.css',
            'css/map/index/multix.css',
            'css/map/index/cookies.css'
        ),
        'output_filename': 'map.min.css',
        'variant': 'datauri',
        }
}

PIPELINE_JS = {
    'map': {
        'source_filenames': (
            'js/map/index/compatibility_check.js',
            # 'vendor/prefixfree.min.js',
            'js/map/index/modernizr.js',
            'vendor/jquery-2.0.3.min.js',
            # 'vendor/leaflet/plugins/jquery.mmenu.js',
            'vendor/hammer.js_v1.0.3/dist/jquery.hammer.min.js',
            'vendor/leaflet/leaflet.js',
            'vendor/leaflet/plugins/L.PolylineDecorator.js',
            # 'vendor/leaflet/plugins/scale.fix.js',
            'vendor/leaflet/plugins/L.GeometryUtil.js',
            'vendor/leaflet/plugins/L.RotatedMarker.js',
            'vendor/leaflet/plugins/L.Symbol.js',
            # 'vendor/leaflet/plugins/leaflet.label.js',
            'vendor/leaflet/plugins/idangerous.swiper-2.0.min.js',
            'vendor/leaflet/plugins/jquery.ba-outside-events.min.js',
            'vendor/leaflet/plugins/ddpanorama.js',
            'vendor/leaflet/plugins/ddpanorama.gensample.js',
            'vendor/cubiq-add-to-homescreen-2.0.8/src/add2home.js',
            'js/helpers/base.js',
            'js/helpers/ajax_helpers.js',
            'js/helpers/resource.js',
            'js/helpers/scroller.js',
            'js/log/logger.js',
            'js/map/index/panorama.js',
            'js/map/index/socialmenu.js',
            'js/map/index/compass.js',
            'js/map/index/helpmenu.js',
            'js/map/index/main.js',
            'js/map/index/jqdialog.min.js',
            'js/map/index/jquery.cookie.js',
            'js/map/index/jquery.cookiecuttr.js',
            'js/map/index/cookiemanager.js',
            'js/helpers/dashboard.js',
            'js/map/index/analyticsmanager.js'
        ),
        'output_filename': 'map.min.js',
        },
    'map2': {
        'source_filenames': (
            'js/map/index/map.js',
        ),
        'output_filename': 'map2.min.js',
        },

    }