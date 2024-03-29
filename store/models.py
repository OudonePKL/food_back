from django.db import models
from users.models import UserModel


class CategoryModel(models.Model):
    class Meta:
        db_table = "category"
        verbose_name_plural = "1. Category types"

    name = models.CharField(max_length=100, default="etc", verbose_name="Category name")

    def __str__(self):
        return str(self.name)


class StoreModel(models.Model):
    class Meta:
        db_table = "store"
        verbose_name_plural = "2. Store list"

    seller = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name="seller")
    name = models.CharField(max_length=100, verbose_name="Store name", )
    address = models.CharField(max_length=200, verbose_name="store location", )
    phone = models.CharField(max_length=200, null=True, blank=True)
    company_number = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Company Registration Number"
    )
    sub_address = models.CharField(max_length=200, verbose_name="Store detailed address", null=True, blank=True)
    introduce = models.TextField(null=True, blank=True, verbose_name="introduction")
    logo1 = models.FileField(null=True, blank=True, verbose_name="logo1", upload_to="media/")
    logo2 = models.FileField(null=True, blank=True, verbose_name="logo2", upload_to="media/")
    background_image = models.FileField(null=True, blank=True, verbose_name="background iamge", upload_to="media/")

    def __str__(self):
        return str(self.name)


class GoodsModel(models.Model):
    class Meta:
        db_table = "goods"
        verbose_name_plural = "3. Product list"

    store = models.ForeignKey(StoreModel, on_delete=models.CASCADE, verbose_name="store")
    category = models.ForeignKey(
        CategoryModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="category",
        default=1,
    )
    name = models.CharField(max_length=100, verbose_name="product name")
    price = models.PositiveIntegerField(default=0, verbose_name="price")
    is_popular = models.BooleanField(default=False, verbose_name="Popular")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


class ImageModel(models.Model):
    class Meta:
        db_table = "image"
        verbose_name_plural = "4. Product image list"

    goods = models.ForeignKey(GoodsModel, on_delete=models.CASCADE, verbose_name="Goods")
    image = models.FileField(null=True, blank=True, verbose_name="image", upload_to="media/")

    def __str__(self):
        return str(self.goods.name)


# Order Old one model
class OrderModel(models.Model):
    class Meta:
        db_table = "order"
        verbose_name_plural = "5. Order History"

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name="buyer")
    goods = models.ForeignKey(
        GoodsModel, on_delete=models.CASCADE, verbose_name="purchase goods"
    )
    price = models.PositiveIntegerField(default=0, verbose_name="price")
    ordered_at = models.DateTimeField(auto_now_add=True, verbose_name="order time")

    def __str__(self):
        return str(self.goods.name)
    
class Cart(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.pk} - User: {self.user.email}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(GoodsModel, on_delete=models.CASCADE, related_name='cartitem')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"CartItem {self.pk} - Product: {self.product.name}, Quantity: {self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    tel = models.CharField(max_length=20)
    total_prices = models.DecimalField(max_digits=10, decimal_places=2)
    account_name = models.CharField(max_length=100, null=True, blank=True)
    province = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    shipping_company = models.CharField(max_length=100, null=True, blank=True)
    branch = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")

    def __str__(self):
        return f"Order {self.pk} - User: {self.user.email}, Status: {self.status}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(GoodsModel, on_delete=models.CASCADE, related_name='orderitem')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"OrderItem {self.pk} - Product: {self.product.name}, Quantity: {self.quantity}"

class ReviewModel(models.Model):
    class Meta:
        db_table = "review"
        verbose_name_plural = "6. Review history"

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name="Writer")
    goods = models.ForeignKey(
        GoodsModel, on_delete=models.CASCADE, verbose_name="review product"
    )
    review = models.TextField()
    star = models.FloatField(default=0, verbose_name="scope")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.goods.name)


class BookmarkModel(models.Model):
    class Meta:
        db_table = "bookmark"
        verbose_name_plural = "Bookmark history"

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    goods = models.ForeignKey(GoodsModel, on_delete=models.CASCADE)
    bookmark = models.BooleanField(default=True)


class FilteringModel(models.Model):
    class Meta:
        verbose_name_plural = "7. Filter product list"

    filter = models.CharField(max_length=100, verbose_name="filter")
    option = models.TextField(null=True, blank=True, default="", verbose_name="Additional explanation")


class PolicyModel(models.Model):
    class Meta:
        verbose_name_plural = "8. Terms and privacy policy"

    category = models.IntegerField(null=True, blank=True, default=1, verbose_name='type')
    content = models.TextField(null=True, blank=True, default='', verbose_name='detail')
