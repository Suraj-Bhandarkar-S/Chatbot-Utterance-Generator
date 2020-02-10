from django.conf.urls import url
from . import views
from django.conf import settings
from django.contrib.auth import views as auth_views

urlpatterns=[
    
    url(r'^$',views.UG,name='UG'),
    url(r'^input/',views.input,name="input"),
    url(r'^rasa/',views.rasa,name="rasa"),
    url(r'^rasa_base/',views.rasa_base,name="rasa1"),
    
]
