from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Product, Category



# 1. Barcha mahsulotlar ro'yxati (Admin uchun)
# class AdminProductListView(View):
#     def get(self, request):
#         products = Product.objects.all().order_by('-id')
#         return render(request, 'admin/admin_products.html', {'products': products})
#

class AdminProductCreateView(View):
    def get(self, request):
        categories = Category.objects.all()
        return render(request, 'admin/admin_product_create.html', {'categories': categories})

    def post(self, request):
        # request.POST.get('nomi', 'default_qiymat')
        category_id = request.POST.get('category')
        title = request.POST.get('title')
        brand = request.POST.get('brand')
        price = request.POST.get('price')

        precent = request.POST.get('precent') or 0
        desc = request.POST.get('desc')
        stock = request.POST.get('stock') or 0
        main_image = request.FILES.get('main_image')

        category = get_object_or_404(Category, id=category_id)

        Product.objects.create(
            category=category,
            title=title,
            brand=brand,
            price=price,
            precent=precent,
            desc=desc,
            stock=stock,
            main_image=main_image
        )
        return redirect('admin_dashboard')


class AdminProductUpdateView(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        categories = Category.objects.all()
        return render(request, 'admin/admin_product_update.html', {
            'product': product,
            'categories': categories
        })

    def post(self, request, pk):
        product = get_object_or_404(Product, id=pk)

        product.title = request.POST.get('title')
        category_id = request.POST.get('category')
        product.category = get_object_or_404(Category, id=category_id)
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.discount_price = request.POST.get('discount_price')


        if request.FILES.get('main_image'):
            product.main_image = request.FILES.get('main_image')

        product.save()
        return redirect('admin_dashboard')



class AdminProductDeleteView(View):
    def get(self, request, id):
        product = get_object_or_404(Product, id=id)
        product.delete()
        return redirect('admin_dashboard')