from django.urls import path
from . import views
from .views import MarketPlaceListView

urlpatterns = [
    # path('', views.index, name='index'),
    path('', MarketPlaceListView.as_view(), name='parser-home'),
    # path('categories/', views.categories, name='categories'),
    # path('urls/', views.urls, name='urls'),
    # path('urls/<int:url_id>/', views.detail_url, name='url_details'),
]

