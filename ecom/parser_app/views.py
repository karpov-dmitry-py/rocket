# from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DetailView

from .models import Category
from .models import Marketplace
from .models import CategoryUrl

class MarketPlaceListView(ListView):
    model = Marketplace
    template_name = 'parser_app/home.html'
    context_object_name = 'marketplaces'
    ordering = ['id']

# def index(request):
#     msg = f'This is the parser app main page'
#     return HttpResponse(msg)
#
#
# def categories(request):
#     items = Category.objects.all()
#     items = [item.name for item in items]
#     # return JsonResponse(items, safe=False)
#     return HttpResponse(items)
#
#
# def urls(request):
#     items = CategoryUrl.objects.all()
#     result = []
#     for item in items:
#         url = {
#             'id': str(item.id),
#             'category': str(item.category),
#             'marketplace': str(item.marketplace),
#             'url': item.url,
#         }
#         result.append(url)
#     # return HttpResponse(result)
#     return JsonResponse(result, safe=False)
#
#
# def detail_url(request, url_id):
#     url_object = CategoryUrl.objects.get(pk=url_id)
#     url = {
#         'id': str(url_object.id),
#         'category': str(url_object.category),
#         'marketplace': str(url_object.marketplace),
#         'url': url_object.url
#     }
#     return JsonResponse(url)
