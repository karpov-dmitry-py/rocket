from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView

from .models import Category
from .models import Marketplace
from .models import CategoryUrl
from .models import ProductUrl


class MarketplaceListView(ListView):
    model = Marketplace
    template_name = 'parser_app/home.html'
    context_object_name = 'marketplaces'
    ordering = ['id']


class MarketplaceCreateView(CreateView):
    model = Category
    fields = ['title', 'content']

# class Marketplace:
#     pass
#
#
# class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#     model = Post
#     fields = ['title', 'content']
