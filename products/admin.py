from django.contrib import admin

from .models import Category, Product, ProductImage, Banner

admin.site.register([ Category,Product,ProductImage,Banner])
