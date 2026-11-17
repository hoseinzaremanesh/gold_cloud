from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('shop/', views.shop, name='shop'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('login/', views.login_page, name='login'),
    path('login/submit/', views.login_view, name='login_submit'),
    path('register/submit/', views.register_view, name='register_submit'),
    path('logout/', views.logout_view, name='logout'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/<str:action>/',
         views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/',
         views.remove_from_cart, name='remove_from_cart'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('order/place/', views.place_order, name='place_order'),
]
