from django.urls import path
from .views import create_instance, destroy_instance
  
urlpatterns = [
    path('create/', create_instance, name='create'),
    path('delete/', destroy_instance, name='delete')
]