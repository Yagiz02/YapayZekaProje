from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('upload_audio/', views.upload_audio, name='upload_audio'),
    path('gallery/', views.gallery, name='gallery'),
]