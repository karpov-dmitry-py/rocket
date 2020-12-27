from django.urls import path

from .views import MarketplaceListView
from .views import MarketplaceDetailView
from .views import MarketplaceCreateView
from .views import MarketplaceUpdateView
from .views import MarketplaceDeleteView

from .views import CategoryListView
from .views import CategoryDetailView
from .views import CategoryCreateView
from .views import CategoryUpdateView
from .views import CategoryDeleteView

from .views import ProductListView
from .views import ProductDetailView
from .views import ProductCreateView
from .views import ProductUpdateView
from .views import ProductDeleteView

urlpatterns = [
    path('', MarketplaceListView.as_view(), name='parser-marketplace-list'),
    path('marketplace/<int:pk>/', MarketplaceDetailView.as_view(), name='parser-marketplace-detail'),
    path('marketplace/add', MarketplaceCreateView.as_view(), name='parser-marketplace-add'),
    path('marketplace/<int:pk>/update/', MarketplaceUpdateView.as_view(), name='parser-marketplace-update'),
    path('marketplace/<int:pk>/delete/', MarketplaceDeleteView.as_view(), name='parser-marketplace-delete'),

    path('category/', CategoryListView.as_view(), name='parser-category-list'),
    path('category/<int:pk>/', CategoryDetailView.as_view(), name='parser-category-detail'),
    path('category/add', CategoryCreateView.as_view(), name='parser-category-add'),
    path('category/<int:pk>/update/', CategoryUpdateView.as_view(), name='parser-category-update'),
    path('category/<int:pk>/delete/', CategoryDeleteView.as_view(), name='parser-category-delete'),

    path('product/', ProductListView.as_view(), name='parser-product-list'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='parser-product-detail'),
    path('product/add', ProductCreateView.as_view(), name='parser-product-add'),
    path('product/<int:pk>/update/', ProductUpdateView.as_view(), name='parser-product-update'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='parser-product-delete'),
]
