from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^simple', views.simpleView, name='simpleView'),
    url(r'^handleMultipleUpload', views.handleMultipleUpload, name='addPics'),
    url(r'^handleDeleteImg', views.handleDeleteImg, name='deletePics'),
    url(r'^$', views.index, name='gallery')

]
