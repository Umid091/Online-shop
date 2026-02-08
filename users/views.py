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
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import Product, User
from products.models import  Product, Category, Banner


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






class LoginView(View):
    def get(self, request):
        return render(request, 'auth/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)


            if str(user.role).upper() == "ADMIN":
                return redirect('admin_dashboard')
            else:
                return redirect('index')

        return render(request, 'auth/login.html', {
            "error": "Username yoki parol xato kiritildi!"
        })


class AdminDashboardView(View):
    def get(self, request):
        products = Product.objects.all().order_by('-id')
        users = User.objects.all().order_by('-id')
        order_items = OrderItem.objects.all().order_by('-id')  # Oxirgi sotuvlar

        # Statistika uchun
        total_sales = sum(item.get_total_price() for item in order_items) if hasattr(order_items,
                                                                                     'get_total_price') else 0

        context = {
            'products': products,
            'users': users,
            'order_items': order_items,
            'total_sales': total_sales,
        }
        return render(request, 'admin/admin_dashboard.html', context)



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





class admin_logaut(View):
    def get(self,request):
        logout(request)
        return redirect('login')


def add_to_cart(request, id):
    product = Product.objects.get(id=id)

    quantity_raw = request.POST.get("quantity", 1)
    quantity = int(quantity_raw)

    cart_item = Cart.objects.filter(user=request.user, product=product).first()
    if cart_item:
        cart_item.quantity += quantity
        cart_item.save()
    else:
        Cart.objects.create(
            user=request.user,
            product=product,
            quantity=quantity
        )

    return redirect('index')

def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items:
        return redirect('index')

    total_price = sum(item.total_price for item in cart_items)

    if request.user.balance < total_price:
        return redirect('index')

    order = Order.objects.create(
        user=request.user
    )

    for item in cart_items:
        OrderItem.objects.create(
            product=item.product,
            order=order,
            quantity=item.quantity,
            price=item.product.price
        )

        item.product.count -= item.quantity  # Agar modelda 'count' bo'lsa
        item.product.save()

    request.user.balance -= total_price
    request.user.save()

    cart_items.delete()

    return redirect('index')


def index(request):
    products = Product.objects.all().order_by('-id')
    categories = Category.objects.all()
    banner = Banner.objects.first()

    cart_items = []
    total_cart_price = 0

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        total_cart_price = sum(item.product.price * item.quantity for item in cart_items)

    context = {
        'products': products,
        'categories': categories,
        'banner': banner,
        'cart_items': cart_items,
        'total_cart_price': total_cart_price,
    }
    return render(request, 'index.html', context)


def remove_cart_item(request, id):
    if request.user.is_authenticated:
        Cart.objects.filter(id=id, user=request.user).delete()

    return redirect('index')

