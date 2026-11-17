from django.db.models import Sum
from .models import CartItem


def cart_count(request):
    total = 0
    if request.user.is_authenticated:
        total = CartItem.objects.filter(
            user=request.user).aggregate(t=Sum('quantity'))['t'] or 0
    return {'cart_count': total}
