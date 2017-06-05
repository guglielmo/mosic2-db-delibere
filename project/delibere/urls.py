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

admin.autodiscover()

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'delibere', views.DeliberaViewSet, base_name='delibere')

schema_view = get_swagger_view(title='DB Delibere API')

urls = [
    url(r'^admin/', admin.site.urls),
    url(r'^docs/', schema_view),
    url(r'^api/upload_file/(?P<filename>.+)$', views.FileUploadView.as_view(), name='upload-file'),
    url(r'^api/token-auth/', obtain_jwt_token, name='obtain-jwt'),
    url(r'^api/token-refresh/', refresh_jwt_token, name='refresh-jwt'),
    url(r'^api/', include(router.urls)),
    url(r'^403$', views.TemplateView.as_view(template_name="403.html"), name='tampering-403'),
    url(r'^$', views.DelibereSearchView.as_view(), name='delibere_search'),
    url(r'^(?P<slug>[\w-]+)/$', views.DeliberaView.as_view(), name='delibera_details'),
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

