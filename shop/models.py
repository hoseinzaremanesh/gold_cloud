from django.db import models
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="دسته بندی")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='عکس')

    def __str__(self):
        return self.name


class Product(models.Model):
    Category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products", verbose_name="دسته بندی")
    name = models.CharField(max_length=100, verbose_name="نام محصول")
    price = models.PositiveIntegerField(verbose_name="قیمت (تومان)")
    image = models.ImageField(upload_to="products/", verbose_name="عکس")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True)

    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(
        default=0, decimal_places=0, max_digits=12)

    def __str__(self):
        return self.name
    
    @property
    def discount_percent(self):
        if self.is_sale and self.sale_price and self.price:
            return round((self.price - self.sale_price) * 100 / self.price)
        return 0

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=11, verbose_name='شماره موبایل')

    def __str__(self):
        return self.user.username
    
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'product')

    def unit_price(self):
        if self.product.is_sale and self.product.sale_price:
            return self.product.sale_price
        return self.product.price

    def total_price(self):
        return self.unit_price() * self.quantity

    def __str__(self):
        return f'{self.user.username} - {self.product.name} x{self.quantity}'
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('processing', 'در حال پردازش'),
        ('shipped', 'ارسال شده'),
        ('delivered', 'تحویل شده'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')

    class Meta:
        ordering = ['-created_at']

    @property
    def number(self):
        return f'EM-{1000 + self.id}'

    def __str__(self):
        return f'{self.number} - {self.user.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.name} x{self.quantity}'