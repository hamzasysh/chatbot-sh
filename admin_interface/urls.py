from django.urls import path
from .views import admin_interface

urlpatterns = [
    path('', admin_interface, name='admin_interface'),
    
]
