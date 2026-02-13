from django.shortcuts import render
from django.views import View
from unicodedata import category

from .models import *
from django.template.context_processors import request
from django.db.models import Q
from users.models import Cart

class HomeView(View):
    def get(self, request):
        products = Product.objects.all().order_by('-id')[:4]
        categories = Category.objects.all()
        banner = Banner.objects.filter(is_active=True).first()
        return render(request, 'index.html', { # Tepada nima yozilsa, bu yerda ham o'sha bo'lishi shart
            'products': products,
            'categories':categories,
            'banner': banner
        })


from django.views import View


class Product_all_view(View):
    def get(self, request):
        query = request.GET.get('q')

        if query:
            products = Product.objects.filter(
                Q(title__icontains=query) | Q(desc__icontains=query)
            )
        else:
            products = Product.objects.all()

        cart_items = []
        total_cart_price = 0
        if request.user.is_authenticated:
            cart_items = Cart.objects.filter(user=request.user)
            total_cart_price = sum(item.product.price * item.quantity for item in cart_items)

        return render(request, 'products_all.html', {
            'products': products,
            'cart_items': cart_items,
            'total_cart_price': total_cart_price,
            'query': query
        })

class About(View):

    def get(self,request):
        return render(request, 'about.html')


class ProductDetails(View):
    def get(self, request, id):
        product = Product.objects.get(id=id)
        related_products = Product.objects.filter(category=product.category).exclude(id=product.id).order_by('-id')[:3]


        cart_items = []
        total_cart_price = 0
        if request.user.is_authenticated:
            cart_items = Cart.objects.filter(user=request.user)
            total_cart_price = sum(item.product.price * item.quantity for item in cart_items)


        return render(request, 'product_detail.html', {
            'product': product,
            'related_products': related_products,
            'cart_items': cart_items,
            'total_cart_price': total_cart_price
        })





