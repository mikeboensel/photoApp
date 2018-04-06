from django.conf.urls import include, url
from django.urls import path, re_path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    re_path(r'^handleMultipleUpload', views.handleMultipleUpload, name='addPics'),
    re_path(r'^handlePicDelete', views.handlePicDelete, name='handlePicDelete'),
    re_path(r'^handlePicLike', views.handlePicLike, name='handlePicLike'),
    re_path(r'^handlePicPrivacyChange', views.handlePicPrivacyChange, name='handlePicPrivacyChange'),
#     url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    path('<str:userName>', views.index, name='gallery')
]
