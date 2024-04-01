import math
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from store.models import (
    StoreModel, GoodsModel, ReviewModel, OrderModel, 
    ImageModel, SizeModel, ColorModel, CategoryModel, 
    ProductImage, Order, OrderItem, 
    BankAccount, Review
    )
from users.models import UserModel

from users.serializers import UserSerializer


def format_with_commas(n):
    return "{:,}".format(int(n))

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryModel
        fields = '__all__'


class GoodsSerializer(serializers.ModelSerializer):
    store_name = serializers.SerializerMethodField()
    star_avg = serializers.SerializerMethodField()
    # category = serializers.SerializerMethodField()
    format_price = serializers.SerializerMethodField()
    review_total = serializers.SerializerMethodField()
    store_address = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    def get_store_name(self, obj):
        store_name = obj.store.name
        if len(store_name) >= 7:
            store_name = f"{store_name[:7]}..."
        return store_name

    def get_star_avg(self, obj):
        review = ReviewModel.objects.filter(goods_id=obj.id).values("star")
        total = 0
        for i in review:
            total += i["star"]

        return math.ceil(total / review.count()) if total != 0 else 0

    # def get_category(self, obj):
    #     return obj.category.name

    def get_format_price(self, obj):
        return str(format_with_commas(obj.price))

    def get_review_total(self, obj):
        # review_total = ReviewModel.objects.filter(goods_id=obj.id).count()
        review_total = Review.objects.filter(product_id=obj.id).count()
        return review_total

    def get_store_address(self, obj):
        address = obj.store.address.split(' ')[:2]
        address = ' '.join(address)
        return address
    
    def get_sizes(self, obj):
        sizes = SizeModel.objects.filter(product=obj)
        serializer = SizeSerializer(sizes, many=True)
        return serializer.data
    
    def get_colors(self, obj):
        colors = ColorModel.objects.filter(product=obj)
        serializer = ColorSerializer(colors, many=True)
        return serializer.data

    def get_image(self, obj):
        image = ImageModel.objects.filter(goods_id=obj.id).first()
        serializer = ImageSerializer(image)
        image = serializer.data.get("image")
        return image
    
    def get_images(self, obj):
        images = ProductImage.objects.filter(product=obj).first()
        serializer = ProductImageSerializer(images)
        images = serializer.data.get("image")
        return images

    class Meta:
        model = GoodsModel
        exclude = ["created_at", "updated_at"]
        # extra_kwargs = {
        #     "category": {"required": False},
        # }


class UpdateStoreSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        name = attrs.get("name")
        if name:
            if len(name) > 15:
                raise ValidationError("Please write your store name in 15 characters or less.")
        return attrs

    class Meta:
        model = StoreModel
        fields = "__all__"
        extra_kwargs = {
            "seller": {"required": False},
        }


class OnlyStoreInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreModel
        exclude = ["seller"]


class StoreSerializer(serializers.ModelSerializer):
    goods_set = serializers.SerializerMethodField()

    # seller = serializers.SerializerMethodField()

    def get_seller(self, obj):
        return obj.seller.email

    def get_goods_set(self, obj):
        goods = GoodsModel.objects.filter(store_id=obj.id)
        serializer = OnlyStoreGoodsSerializer(goods, many=True)
        return serializer.data

    class Meta:
        model = StoreModel
        fields = "__all__"


# old review
# class ReviewSerializer(serializers.ModelSerializer):
#     profile_image = serializers.SerializerMethodField()
#     created_at = serializers.SerializerMethodField()
#     nickname = serializers.SerializerMethodField()

#     def validate(self, attrs):
#         review = attrs.get("review")
#         if review:
#             if len(review) < 10:
#                 raise ValidationError("Please register your review with at least 10 characters.")
#         return attrs

#     def get_profile_image(self, obj):
#         user = UserModel.objects.get(id=obj.user.id)
#         if not user.profile_image:
#             return None
#         else:
#             return user.profile_image.url

#     def get_created_at(self, obj):
#         return obj.created_at.strftime("%Y.%m.%d")

#     def get_nickname(self, obj):
#         return obj.user.nickname

#     class Meta:
#         # model = ReviewModel
#         model = Review
#         exclude = ["updated_at", "product"]
#         extra_kwargs = {
#             "user": {"required": False},
#             "product": {"required": False},
#         }

# new review
class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Review
        fields = '__all__'

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'   

class GoodsDetailSerializer(serializers.ModelSerializer):
    """
     Replace store with name
     Create a review set for the product
     """

    store_name = serializers.SerializerMethodField()
    store_user_id = serializers.SerializerMethodField()
    review_set = serializers.SerializerMethodField()
    # category = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()
    image_set = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    format_price = serializers.SerializerMethodField()
    star_avg = serializers.SerializerMethodField()
    store_image = serializers.SerializerMethodField()
    store_id = serializers.SerializerMethodField()

    def get_store_name(self, obj):
        return obj.store.name

    def get_store_id(self, obj):
        return obj.store.id

    def get_review_set(self, obj):
        # review = ReviewModel.objects.filter(goods_id=obj.id).order_by("-created_at")
        review = Review.objects.filter(product_id=obj.id).order_by("-created_at")
        serializer = ReviewSerializer(review, many=True)
        return serializer.data

    # def get_category(self, obj):
    #     return obj.category.name
    
    def get_sizes(self, obj):
        sizes = SizeModel.objects.filter(product=obj)
        serializer = SizeSerializer(sizes, many=True)
        return serializer.data
    
    def get_colors(self, obj):
        colors = ColorModel.objects.filter(product=obj)
        serializer = ColorSerializer(colors, many=True)
        return serializer.data

    def get_image_set(self, obj):
        images = ImageModel.objects.filter(goods_id=obj.id)
        serializer = ImageSerializer(images, many=True)
        image_set = [i['image'] for i in serializer.data]
        return image_set
    
    def get_images(self, obj):
        images = ProductImage.objects.filter(product=obj).first()
        serializer = ProductImageSerializer(images)
        images = serializer.data.get("image")
        return images

    def get_address(self, obj):
        address = obj.store.address
        # address = obj.store.address.split(' ')[:2]
        # address = ' '.join(address)
        return address

    def get_store_user_id(self, obj):
        return obj.store.seller.id

    # def get_price(self, obj):
    #     return str(format_with_commas(obj.price))
    
    def get_price(self, obj):
        return obj.price

    def get_store_image(self, obj):
        return obj.store.seller.profile_image.url if obj.store.seller.profile_image else False

    def get_star_avg(self, obj):
        review = ReviewModel.objects.filter(goods_id=obj.id).values("star")
        total = 0
        for i in review:
            total += i["star"]

        return math.ceil(total / review.count()) if total != 0 else 0

    def get_format_price(self, obj):
        return str(format_with_commas(obj.price))

    class Meta:
        model = GoodsModel
        exclude = ["created_at", "updated_at"]

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeModel
        fields = '__all__'

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorModel
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = "__all__"
        extra_kwargs = {
            "goods": {"required": False},
        }

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'
        

# Order
class OrderItemSerializer(serializers.ModelSerializer):
    product = GoodsSerializer()
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'color', 'size']

class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    def get_items(self, obj):
        order_items = OrderItem.objects.filter(order=obj)
        serializer = OrderItemSerializer(order_items, many=True)
        return serializer.data

    class Meta:
        model = Order
        fields = ['id', 'user', 'tel', 'total_prices', 'account_name', 'province', 'district', 'shipping_company', 'branch', 'created_at', 'status', 'items']


class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'color', 'size']

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)

    def create(self, validated_data):
        order_items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for order_item_data in order_items_data:
            OrderItem.objects.create(order=order, **order_item_data)
        return order

    class Meta:
        model = Order
        fields = ['id', 'user', 'tel', 'total_prices', 'account_name', 'province', 'district', 'shipping_company', 'branch', 'created_at', 'status', 'items']


class PendingOrderSerializer(OrderSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'tel', 'total_prices', 'account_name', 'province', 'district', 'shipping_company',
                  'branch', 'created_at', 'status', 'items']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.status != 'Pending':
            return None  # Skip orders that are not pending
        return data


class ProcessingOrderSerializer(OrderSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'tel', 'total_prices', 'account_name', 'province', 'district', 'shipping_company',
                  'branch', 'created_at', 'status', 'items']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.status != 'Processing':
            return None  # Skip orders that are not processing
        return data

class DeliveredOrderSerializer(OrderSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'tel', 'total_prices', 'account_name', 'province', 'district', 'shipping_company',
                  'branch', 'created_at', 'status', 'items']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.status != 'Delivered':
            return None  # Skip orders that are not Delivered
        return data


class ShippedOrderSerializer(OrderSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'tel', 'total_prices', 'account_name', 'province', 'district', 'shipping_company',
                  'branch', 'created_at', 'status', 'items']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.status != 'Shipped':
            return None  # Skip orders that are not Shipped
        return data

class OrderItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'color', 'size']

class OrderUpdateSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        # Update order fields
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        return instance

    class Meta:
        model = Order
        fields = ['status']

class PostSerializer(serializers.Serializer):
    name = serializers.CharField(help_text="product name")
    price = serializers.IntegerField(help_text="product price")

    review = serializers.CharField(help_text="Review contents")

    search = serializers.CharField(help_text="What to search for")

    goods_id = serializers.IntegerField(help_text="Product ID to order")


class OnlyStoreGoodsSerializer(serializers.ModelSerializer):
    """
     Replace store with name
     Create a review set for the product
     """
    review_set = serializers.SerializerMethodField()
    # category = serializers.SerializerMethodField()
    order_set = serializers.SerializerMethodField()
    goods_id = serializers.SerializerMethodField()
    image_set = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    format_price = serializers.SerializerMethodField()
    star_avg = serializers.SerializerMethodField()

    def get_store(self, obj):
        return obj.store.name

    def get_review_set(self, obj):
        # review = ReviewModel.objects.filter(goods_id=obj.id).order_by("-created_at")
        review = Review.objects.filter(product_id=obj.id).order_by("-created_at")
        serializer = OnlyStoreReviewSerializer(review, many=True)
        return serializer.data

    # def get_category(self, obj):
    #     return obj.category.name

    def get_order_set(self, obj):
        order = OrderModel.objects.filter(goods_id=obj.id).order_by("-ordered_at")
        serializer = OrderSerializer(order, many=True)
        return serializer.data

    def get_goods_id(self, obj):
        return obj.id

    def get_image_set(self, obj):
        images = ImageModel.objects.filter(goods_id=obj.id)
        serializer = ImageSerializer(images, many=True)
        image_set = [i['image'] for i in serializer.data]
        return image_set
    
    def get_images(self, obj):
        images = ProductImage.objects.filter(product=obj).first()
        serializer = ProductImageSerializer(images)
        images = serializer.data.get("image")
        return images

    def get_format_price(self, obj):
        return str(format_with_commas(obj.price))

    def get_star_avg(self, obj):
        review = ReviewModel.objects.filter(goods_id=obj.id).values("star")
        total = 0
        for i in review:
            total += i["star"]

        return math.ceil(total / review.count()) if total != 0 else 0

    class Meta:
        model = GoodsModel
        fields = ["star_avg","goods_id", "review_set", "category", "order_set", "name", "price", "format_price", "image_set", "images", "description"]


class OnlyStoreReviewSerializer(serializers.ModelSerializer):
    review_id = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    goods_id = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    user_profile = serializers.SerializerMethodField()

    def get_review_id(self, obj):
        return obj.id

    def get_user_name(self, obj):
        return obj.user.nickname

    def get_goods_id(self, obj):
        return obj.goods.id

    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y.%m.%d")

    def get_user_profile(self, obj):
        return obj.user.profile_image.url if obj.user.profile_image else None

    class Meta:
        model = ReviewModel
        exclude = ["updated_at", "goods", "id"]
        extra_kwargs = {
            "user": {"required": False},
            "goods": {"required": False},
        }


class ChatStoreSerializer(serializers.Serializer):
    class Meta:
        model = StoreModel
        exclude = ["created_at", "updated_at"]


class GoodsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsModel
        exclude = ["store", "category"]
        # extra_kwargs = {
        #     "description": {"required": False},
        # }

class CreateProductSerializer(serializers.ModelSerializer):
    sizes = serializers.ListField(child=serializers.CharField(max_length=50), write_only=True)
    colors = serializers.ListField(child=serializers.CharField(max_length=50), write_only=True)
    images = serializers.ListField(child=serializers.ImageField(), write_only=True)

    class Meta:
        model = GoodsModel
        fields = ['name', 'description', 'price', 'category', 'store', 'sizes', 'colors', 'images']

    def create(self, validated_data):
        sizes_data = validated_data.pop('sizes', [])
        colors_data = validated_data.pop('colors', [])
        images_data = validated_data.pop('images', [])

        product = GoodsModel.objects.create(**validated_data)

        for size_name in sizes_data:
            SizeModel.objects.create(product_id=product.id, name=size_name)

        for color_name in colors_data:
            ColorModel.objects.create(product_id=product.id, name=color_name)

        for image_file in images_data:
            ProductImage.objects.create(product_id=product.id, image=image_file)

        return product
    
class UpdateProductSerializer(serializers.ModelSerializer):
    sizes = serializers.ListField(child=serializers.CharField(max_length=50), required=False)
    colors = serializers.ListField(child=serializers.CharField(max_length=50), required=False)
    images = serializers.ListField(child=serializers.ImageField(), required=False)

    class Meta:
        model = GoodsModel
        fields = ['name', 'description', 'price', 'category', 'sizes', 'colors', 'images']

    def update(self, instance, validated_data):
        sizes_data = validated_data.pop('sizes', None)
        colors_data = validated_data.pop('colors', None)
        images_data = validated_data.pop('images', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if sizes_data is not None:
            instance.size.all().delete()  # Clear existing sizes
            for size_name in sizes_data:
                SizeModel.objects.create(product=instance, name=size_name)

        if colors_data is not None:
            instance.color.all().delete()  # Clear existing colors
            for color_name in colors_data:
                ColorModel.objects.create(product=instance, name=color_name)

        if images_data is not None:
            instance.images.all().delete()  # Clear existing images
            for image_file in images_data:
                ProductImage.objects.create(product=instance, image=image_file)

        return instance
    
# bank account
class BankAccountSerializer(serializers.ModelSerializer):
    # Assuming 'store' is a ForeignKey field in your BankAccount model
    
    # Use PrimaryKeyRelatedField if store is represented by its ID
    store = serializers.PrimaryKeyRelatedField(queryset=StoreModel.objects.all())

    class Meta:
        model = BankAccount
        fields = ['id', 'name', 'account_name', 'account_number', 'image', 'store']

class BankAccountSerializer2(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'


class BankAccountByStoreSerializer(serializers.Serializer):
    has_bank_account = serializers.SerializerMethodField()

    def get_has_bank_account(self, obj):
        return obj

# class BankAccountDetailByStoreSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BankAccount
#         fields = ['id', 'name', 'account_name', 'account_number', 'image']