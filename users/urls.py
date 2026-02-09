from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('email-verify/', views.EmailVerifyView.as_view(), name='email_verify'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/',views.ProfileView.as_view(),name='profile'),
    path('admin/',views.AdminDashboardView.as_view(),name='admin_dashboard'),
    path('admin-logout/', views.admin_logaut.as_view(), name='admin_logout'),
    path('cart/add/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('', views.index, name='index'),
    path('cart/remove/<int:id>/', views.remove_cart_item, name='remove_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.my_orders, name='my_orders'),

    # path('add_to_cart/<int:id>', views.add_to_cart, name='add_to_cart'),
    # path('checkout/', views.checkout, name='checkout'),
]