from django.shortcuts import render
from .models import Category, Product, CartItem
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect
from .models import Profile, CartItem, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from django.views.decorators.http import require_POST


def landing(request):
    products = Product.objects.all()[:4]
    categories = Category.objects.all()
    return render(request, 'landing.html', {
        'products': products,
        'categories': categories,

    })


def shop(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    deals = Product.objects.filter(is_sale=True)[:8]
    best_sellers = Product.objects.all()[:4]

    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(Category_id=category_id)

    return render(request, 'shop.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'deals': deals,
        'best_sellers': best_sellers,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related = Product.objects.filter(
        Category=product.Category).exclude(id=product.id)[:4]
    return render(request, 'pro.html', {
        'product': product,
        'related': related,
    })


def login_page(request):
    if request.user.is_authenticated:
        return redirect('landing')
    return render(request, 'login.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('landing')
        messages.error(
            request, 'نام کاربری یا رمز عبور اشتباه است.', extra_tags='login')
    return redirect('login')


def register_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        username = request.POST.get('username', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not username or not password:
            messages.error(
                request, 'نام کاربری و رمز عبور الزامی است.', extra_tags='register')
        elif password != password2:
            messages.error(
                request, 'رمز عبور و تکرار آن یکسان نیست.', extra_tags='register')
        elif User.objects.filter(username=username).exists():
            messages.error(
                request, 'این نام کاربری قبلاً استفاده شده است.', extra_tags='register')
        else:
            user = User.objects.create_user(
                username=username, password=password, first_name=full_name)
            Profile.objects.create(user=user, phone=phone)
            login(request, user)
            return redirect('landing')
    return redirect('login')


def logout_view(request):
    logout(request)
    return redirect('landing')


@login_required(login_url='login')
def cart_view(request):
    items = CartItem.objects.filter(
        user=request.user).select_related('product')
    total = sum(item.total_price() for item in items)
    tax = int(total * 8 / 100)
    grand_total = total + tax
    return render(request, 'shoppingcart.html', {
        'items': items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
    })


@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        qty = int(request.GET.get('qty', 1))
    except ValueError:
        qty = 1
    qty = max(1, min(qty, 10))

    item, created = CartItem.objects.get_or_create(
        user=request.user, product=product, defaults={'quantity': qty}
    )
    if not created:
        item.quantity += qty
        item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        count = CartItem.objects.filter(
            user=request.user).aggregate(t=Sum('quantity'))['t'] or 0
        return JsonResponse({'count': count})

    return redirect(request.META.get('HTTP_REFERER', 'cart'))


@login_required(login_url='login')
def update_cart(request, item_id, action):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if action == 'plus':
        item.quantity += 1
        item.save()
    elif action == 'minus':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
    return redirect('cart')


@login_required(login_url='login')
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect('cart')


@login_required(login_url='login')
def dashboard(request):
    profile = Profile.objects.filter(user=request.user).first()
    items = CartItem.objects.filter(
        user=request.user).select_related('product')
    return render(request, 'dashboard.html', {
        'profile': profile,
        'items': items,
    })


DELIVERY_COSTS = {'standard': 0, 'express': 2500000, 'luxury': 4500000}
PROMO_RATES = {'EMERALD10': 10, 'VIP20': 20}


@login_required(login_url='login')
@require_POST
def place_order(request):
    items = CartItem.objects.filter(
        user=request.user).select_related('product')
    if not items.exists():
        return JsonResponse({'error': 'سبد خرید خالی است.'}, status=400)

    subtotal = sum(item.total_price() for item in items)
    tax = int(subtotal * 8 / 100)
    delivery = DELIVERY_COSTS.get(request.POST.get('delivery'), 0)
    discount = int(
        subtotal * PROMO_RATES.get(request.POST.get('promo', ''), 0) / 100)
    total = subtotal + tax + delivery - discount

    order = Order.objects.create(user=request.user, total=total)
    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            name=item.product.name,
            price=item.unit_price(),
            quantity=item.quantity,
        )
    items.delete()

    return JsonResponse({'number': order.number, 'total': total})
