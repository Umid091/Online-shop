from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from .models import *
import random
from django.conf import settings
from django.core.mail import send_mail
from .models import User



class RegisterView(View):
    def get(self, request):
        return render(request, 'auth/register.html')

    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password']
        password2 = request.POST['confirm_password']

        if User.objects.filter(username=username).exists():
            return render(request, 'auth/register.html', {
                "error":"Bu username band"
            })

        if password1 != password2:
            return render(request, 'auth/register.html', {
                "error": "Parollar mos emas"
            })

        if User.objects.filter(email=email).exists():
            return render(request, 'auth/register.html', {
                "error": "Bu email ishlatilgan"
            })

        User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            is_active=False
        )
        code = str(random.randint(100000, 999999))

        send_mail(
            "Tasdiqlash kodi",
            f"Sizning tasdiqlash kodingiz {code}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        email_verify = EmailVerify.objects.create(
            email=email,
            code=code,
        )
        email_verify.save()

        request.session['email'] = email
        return redirect('email_verify')



class EmailVerifyView(View):
    def get(self, request):
        return render(request, 'auth/email_verify.html')

    def post(self, request):
        confirm_code = request.POST['code']
        email = request.session.get('email')

        email_verify = EmailVerify.objects.filter(email=email, is_confirmed=False).first()

        if confirm_code != email_verify.code:
            return render(request, 'auth/email_verify.html', {
                "error": "Tasdiqlash kodi xato"
            })

        now = timezone.now()
        if now > email_verify.expiration_time:
            return render(request, 'auth/email_verify.html', {
                "error": "Kodni yaroqli muddati tugagan"
            })

        email_verify.is_confirmed = True
        email_verify.save()

        user = User.objects.get(email=email)
        user.is_active = True
        user.save()

        request.session.flush()
        return redirect('login')


from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import Product, User


# 1. Login qismi
class LoginView(View):
    def get(self, request):
        return render(request, 'auth/login.html')

    def post(self, request):
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)

        if user:
            login(request, user)
            if user.role == User.Role.ADMIN:
                return redirect('admin_dashboard')
            return redirect('index')
        return render(request, 'auth/login.html', {"error": "Xato!"})


class AdminDashboardView(View):
    def get(self, request):
        if not request.user.is_authenticated or request.user.role != User.Role.ADMIN:
            return redirect('login')

        products = Product.objects.all().order_by('-id')
        return render(request, 'admin/dashboard.html', {'products': products})


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect
from .models import User


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'auth/profile.html')

    def post(self, request):
        user = request.user

        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')
        user.age = request.POST.get('age') or None
        if request.FILES.get('image'):
            user.image = request.FILES.get('image')

        user.save()
        return redirect('profile')