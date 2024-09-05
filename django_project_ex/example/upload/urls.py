from django.urls import path

from example.upload import views

app_name = 'upload'

urlpatterns = [
    path('private/', views.private, name='private'),
    path('public/', views.public, name='public'),
    path('invalid/', views.invalid, name='invalid'),
]
