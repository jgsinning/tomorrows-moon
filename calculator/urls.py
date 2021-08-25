from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('calc', views.calculation, name='calc'),
    url(r'references', views.references, name='references'),
    url(r'accuracy', views.accuracy, name='accuracy'),
]
