from django.conf.urls import include, url
from django.urls import path, re_path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    re_path(r'^handleMultipleUpload', views.handleMultipleUpload, name='addPics'),
    re_path(r'^handlePicDelete', views.handlePicDelete, name='handlePicDelete'),
    re_path(r'^handlePicLike', views.handlePicLike, name='handlePicLike'),
    re_path(r'^handlePicPrivacyChange', views.handlePicPrivacyChange, name='handlePicPrivacyChange'),
    re_path(r'^handlePicCommentAction', views.handlePicCommentAction, name='handlePicCommentAction'),
    re_path(r'^getPicComments/$', views.getPicComments, name='getPicComments'),
    re_path(r'(?P<userName>\w+)[/]?$', views.index, name='gallery'),

#     re_path('<str:userName>', views.index, name='gallery'),
#     path('', views.index, name='gallery'),
#     url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home')
]
