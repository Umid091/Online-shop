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
from django.shortcuts import get_object_or_404
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import Product, User,WishList
from products.models import  Product, Category, Banner
from django.contrib import messages

class RegisterView(View):
    def get(self, request):
        return render(request, 'auth/register.html')

    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password']
        password2 = request.POST['confirm_password']
        print(f"111111111DEBUG: Username: {username}, Email: {email}")

        # 1. Username bandligini tekshirish
        if User.objects.filter(username=username).exists():
            return render(request, 'auth/register.html', {"error": "Bu username band"})

        # 2. Email bandligini tekshirish (BU QATORNI TEPAGA CHIQARDIM)
        if User.objects.filter(email__iexact=email).exists():
            found_user = User.objects.filter(email__iexact=email).first()
            print(f"XATO: Email bazada bor! Uni ishlatayotgan user: {found_user.username}")
            return render(request, 'auth/register.html', {"error": "Bu email ishlatilgan"})
        # 3. Parollar mosligini tekshirish
        if password1 != password2:
            return render(request, 'auth/register.html', {"error": "Parollar mos emas"})

        # FAQAT HAMMA TEKSHIRUVDAN O'TGANDAN KEYIN USER YARATAMIZ
        user = User.objects.create_user(
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

        # EmailVerify yaratish
        EmailVerify.objects.create(
            email=email,
            code=code,
        )


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
    if not request.user.is_authenticated:
        return redirect('/auth/login')
    product = Product.objects.get(id=id)

    quantity_raw = request.POST.get("quantity")
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


from django.shortcuts import redirect, render
from django.db import transaction
from .models import Cart, Order, OrderItem


def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')

    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        print("XATO: Savat bo'sh!")
        return redirect('index')

    total_sum = sum(item.total_price for item in cart_items)

    # Balansni tekshirishda xatolikni oldini olish
    user_balance = request.user.balance if request.user.balance is not None else 0

    if user_balance < total_sum:
        messages.error(request, "Mablag'ingiz yetarli emas!")
        return redirect('index')

    try:
        with transaction.atomic():
            order = Order.objects.create(user=request.user)

            for item in cart_items:
                real_price = item.product.discount_price if item.product.precent > 0 else item.product.price

                # Ombor zaxirasini tekshirish
                if item.product.stock < item.quantity:
                    print(f"XATO: {item.product.title} omborda yetarli emas!")
                    raise Exception(f"{item.product.title} yetarli emas")

                OrderItem.objects.create(
                    product=item.product,
                    order=order,
                    quantity=item.quantity,
                    price=real_price
                )

                item.product.stock -= item.quantity
                item.product.save()

            request.user.balance -= total_sum
            request.user.save()
            cart_items.delete()

        return redirect('my_orders')

    except Exception as e:
        messages.error(request, f"Xatolik: {str(e)}")
        return redirect('index')
    except Exception as e:
        return redirect('index')


def my_orders(request):
    if not request.user.is_authenticated:
        return redirect('login')

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})

def index(request):
    products = Product.objects.all().order_by('-id')
    categories = Category.objects.all()
    banner = Banner.objects.first()

    cart_items = []
    total_cart_price = 0

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        total_cart_price = sum(item.product.price * item.quantity for item in cart_items)

    wishlist_product_ids = []
    if request.user.is_authenticated:
        # Userning wishlistidagi mahsulotlarni ID larini olamiz
        wishlist_product_ids = request.user.wishlist.values_list('product_id', flat=True)


    context = {
        'products': products,
        'categories': categories,
        'banner': banner,
        'cart_items': cart_items,
        'total_cart_price': total_cart_price,
        'wishlist_product_ids': wishlist_product_ids,
    }
    return render(request, 'index.html', context)


def remove_cart_item(request, id):
    if request.user.is_authenticated:
        Cart.objects.filter(id=id, user=request.user).delete()

    return redirect('index')






def toggle_wishlist(request, id):
    if not request.user.is_authenticated:
        return redirect('login')

    product = get_object_or_404(Product, id=id)
    wishlist_item = WishList.objects.filter(user=request.user, product=product).first()

    if wishlist_item:
        wishlist_item.delete()  # Agar allaqachon bo'lsa, o'chiradi
    else:
        WishList.objects.create(user=request.user, product=product)  # Bo'lmasa, qo'shadi

    # Kelgan sahifasiga qaytarib yuboradi
    return redirect(request.META.get('HTTP_REFERER', 'index'))



def my_wishlist(request):
    # Foydalanuvchining saralangan mahsulotlarini olish
    wishlist_items = WishList.objects.filter(user=request.user)

    return render(request, 'wishlist.html', {
        'wishlist_items': wishlist_items
    })


from django.shortcuts import redirect, get_object_or_404
from .models import Product, Comment


def add_comment(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        comment_body = request.POST.get('body')  # HTML dagi name="body" dan oladi

        if request.user.is_authenticated and comment_body:
            Comment.objects.create(
                product=product,
                user=request.user,
                body=comment_body,
                is_active=True  # Default True bo'lsa ham, aniqlik uchun
            )
        return redirect('product_detail', id=product_id)


from django.contrib.auth import logout


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('index')
    return redirect('index')