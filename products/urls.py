from django.urls import path
from .views import HomeView,Product_all_view,About,ProductDetails

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('products/',Product_all_view.as_view(),name='products_all' ),
    path('about/', About.as_view(), name='about'),
    path('product-detail/<int:id>/',ProductDetails.as_view(),name='product_detail')
]