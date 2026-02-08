from django.shortcuts import render
from django.views import View
from unicodedata import category

from .models import *
from django.template.context_processors import request

class HomeView(View):
    def get(self, request): # To'g'ri yozilishi: request
        products = Product.objects.all().order_by('-id')[:4]
        categories = Category.objects.all() # Faqat 3 ta kategoriya
        banner = Banner.objects.filter(is_active=True).first()
        return render(request, 'index.html', { # Tepada nima yozilsa, bu yerda ham o'sha bo'lishi shart
            'products': products,
            'categories':categories,
            'banner': banner
        })


class Product_all_view(View):
    def get(self,request):
        products=Product.objects.all()
        return render(request, 'products_all.html',{
            'products':products
        })

class About(View):

    def get(self,request):
        return render(request, 'about.html')


class ProductDetails(View):
    def get(self, request,  id):
        product=Product.objects.get(id=id)
        related_products=Product.objects.filter(category=product.category).exclude(id=product.id).order_by('-id')[:3]
        return render(request, 'product_detail.html', {
            'product': product,
            'related_products': related_products
        })


