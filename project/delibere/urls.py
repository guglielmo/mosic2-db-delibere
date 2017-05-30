# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url

# load admin modules
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from rest_framework_swagger.views import get_swagger_view

import views
# from views import DeliberaViewSet, FileUploadView

admin.autodiscover()

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter(trailing_slash=False)
# router.register(r'delibere', DeliberaViewSet, base_name='delibere')

schema_view = get_swagger_view(title='DB Delibere API')

urls = [
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^search/', include('haystack.urls')),
    url(r'^docs/', schema_view),
    # url(r'^upload_file/(?P<filename>.+)$', FileUploadView.as_view(), name='upload-file'),
    url(r'^api-token-auth/', obtain_jwt_token, name='obtain-jwt'),
    url(r'^api-token-refresh/', refresh_jwt_token, name='refresh-jwt'),
    url(r'^403$', views.TemplateView.as_view(template_name="403.html"), name='tampering-403'),
]
urlpatterns = urls

# static and media urls with DEBUG = True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns.append(
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )

