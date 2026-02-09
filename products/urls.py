from django.urls import path
from .views import HomeView,Product_all_view,About,ProductDetails
from .admin_view import  AdminProductCreateView, AdminProductUpdateView, AdminProductDeleteView
urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('products/',Product_all_view.as_view(),name='products_all' ),
    path('about/', About.as_view(), name='about'),
    path('product-detail/<int:id>/',ProductDetails.as_view(),name='product_detail'),

    path('admin-panel/products/add/', AdminProductCreateView.as_view(), name='admin_product_create'),
    path('admin-panel/products/edit/<int:pk>/', AdminProductUpdateView.as_view(), name='admin_product_update'),
    path('admin-panel/products/delete/<int:id>/', AdminProductDeleteView.as_view(), name='admin_product_delete'),


]