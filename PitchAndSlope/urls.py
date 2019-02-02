from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from PitchAndSlope.core import views as coreviews


urlpatterns = [
    url(r'^$', coreviews.home, name='home'),
     url(r'^userHome/$', coreviews.userHome, name='userHome'),
    url(r'^uploadImage/$', coreviews.uploadImage, name='uploadImage'),
    url(r'^signup/$', coreviews.signup, name='signup'),
    url(r'^processImage/$', coreviews.processImage, name='processImage'),
    url(r'^processLogin/$', coreviews.processLogin, name='processLogin'),
    url(r'^viewImage/$', coreviews.viewImage, name='viewImage'),
    url(r'^saveImage/$', coreviews.saveImage, name='saveImage'),
    url(r'^logout/$', coreviews.logout, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
