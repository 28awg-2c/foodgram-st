from django.urls import path
from . import views

app_name = 'static_page'

urlpatterns = [
    path('about/', views.about, name='about'),
    path('tech/', views.tech, name='tech'),
]