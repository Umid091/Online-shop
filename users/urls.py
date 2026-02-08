from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('email-verify/', views.EmailVerifyView.as_view(), name='email_verify'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/',views.ProfileView.as_view(),name='profile')
    # path('add_to_cart/<int:id>', views.add_to_cart, name='add_to_cart'),
    # path('checkout/', views.checkout, name='checkout'),
]