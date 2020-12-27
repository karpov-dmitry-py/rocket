from django.urls import path
from .views import MarketplaceListView
from .views import MarketplaceCreateView

urlpatterns = [
    path('', MarketplaceListView.as_view(), name='parser-marketplace-list'),
    path('marketplace/add', MarketplaceCreateView.as_view(), name='parser-marketplace-add'),
]
