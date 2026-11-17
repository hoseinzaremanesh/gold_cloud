from django.contrib import admin
from .models import Category, Product, Profile , CartItem ,Order, OrderItem


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Profile)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)