from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('categories/', views.categories, name='categories'),
    path('urls/', views.urls, name='urls'),
    path('urls/<int:url_id>/', views.detail_url, name='url_details'),
]

