import base64
import uuid
from collections import Counter
from pprint import pprint
from PIL import Image
import io
import django
from django.core.files.base import ContentFile
from django.db.models import Q, Count
from django.shortcuts import render, redirect
from rest_framework import status, permissions, generics, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from .form import ReviewForm
from .models import (
    GoodsModel,
    StoreModel,
    ReviewModel,
    BookmarkModel,
    OrderModel, Order, OrderItem,
    FilteringModel, ImageModel, CategoryModel, PolicyModel,
    Cart, CartItem
)
from .serializers import (
    StoreSerializer,
    GoodsSerializer,
    ReviewSerializer,
    GoodsDetailSerializer,
    PostSerializer,
    UpdateStoreSerializer,
    ImageSerializer,
    GoodsCreateSerializer,
    OrderSerializer, OrderCreateSerializer, OrderUpdateSerializer, PendingOrderSerializer, ProcessingOrderSerializer, ShippedOrderSerializer, DeliveredOrderSerializer, 
    CartSerializer, CreateCartSerializer, CartUpdateSerializer,
    GoodsEditSerializer,
)

from drf_yasg.utils import swagger_auto_schema

"""
Permission to divide general users, merchants, and administrators
"""


class IsSeller(BasePermission):
    def has_permission(self, request, view):
        try:
            seller = request.user.is_seller
            admin = request.user.is_admin
            if seller or admin:
                return True
            else:
                return False
        except:
            # Login
            return False


def goods_list(request):
    return render(request, 'home.html')


def goods_detail(request, goods_id):
    return render(request, 'store/goods_detail.html')


def order_list(request):
    return render(request, 'store/order_list.html')


def store_setting(request):
    return render(request, 'store/admin.html')


class GoodsView(APIView):
    @swagger_auto_schema(tags=["View product list and details"], responses={200: "Success"})
    def get(self, request, goods_id=None):
        """
         <View product>
         goods_id O -> View details
         goods_id
         * Separately removed due to merchant permission issues *
         """
        if goods_id is None:
            category = request.GET.get('category', '1')  # You can provide default values.
            goods = GoodsModel.objects.all()
            if not goods.exists():
                return Response([], status=200)
            """
             <Filtering branch>
             - Latest
             - Old shoots
             - Price ascending & descending order
             - Ascending & descending number of reviews (5,6)
             """
            if category == '2':
                goods = goods.order_by(
                    "-price"
                )
            elif category == '3':
                goods = goods.annotate(review_count=Count("reviewmodel")).order_by(
                    "-review_count"
                )
            elif category == '4':
                goods = goods.order_by(
                    "price"
                )
            elif category == '5':
                goods = goods.annotate(order_count=Count("ordermodel")).order_by(
                    "-order_count"
                )
            elif category == '6':
                goods = goods.annotate(order_count=Count("ordermodel")).order_by(
                    "-created_at"
                )
            elif category == '7':
                goods = goods.filter(is_popular=True).order_by(
                    "-created_at"
                )
            else:
                try:
                    goods = goods.order_by("-price")
                except Exception as e:
                    print(e)
                    return Response(
                        {"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
                    )
            serializer = GoodsSerializer(goods, many=True)
            return Response(serializer.data, status=200)
            # return render(request, 'home.html', context={'data': serializer.data, "token": token})
        else:
            goods = get_object_or_404(GoodsModel, id=goods_id)
            serializer = GoodsDetailSerializer(goods)
            order_total = OrderModel.objects.filter(user_id=request.user.id, goods=goods).count()
            review_total = ReviewModel.objects.filter(user_id=request.user.id, goods=goods).count()
            result = serializer.data.copy()
            if order_total >= review_total:
                result['is_ordered'] = True
            else:
                result['is_ordered'] = False
            return Response(result, status=200)
            # return render(request, 'store/goods_detail.html', context={'goods': serializer.data})


class StoreView(APIView):
    # permission_classes = [IsSeller]

    @swagger_auto_schema(tags=["Store information & product registration & store modification"], responses={200: "Success"})
    def get(self, request, store_id):
        """
         <View store information>
         - Store basic information
         - List of products in the store
         """
        store = get_object_or_404(StoreModel, id=store_id)
        serializer = StoreSerializer(store)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Store information & product registration & store modification"],
        request_body=PostSerializer,
        responses={200: "Success"},
    )
    def post(self, request, store_id):
        """
         <Product Registration>
         Will be converted to multiple images
         """
        if request.data.get('goods_set'):
            for data in request.data.get("goods_set"):
                if data:
                    serializer = GoodsCreateSerializer(data=data)
                    category, is_created = CategoryModel.objects.get_or_create(name=data.get('category'))
                    if serializer.is_valid():
                        instance = serializer.save(category=category, store_id=store_id)
                        images_data = data.get('images', [])
                        if images_data:
                            for image_data in images_data:
                                format, imgstr = image_data.split(';base64,')
                                ext = format.split('/')[-1]
                                file_data = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
                                ImageModel.objects.create(goods=instance, image=file_data)
            return Response({"message": "The product has been registered."}, status=status.HTTP_201_CREATED)
        return Response({"message": "A problem has occurred."}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Store information & product registration & store modification"],
        request_body=PostSerializer,
        responses={200: "Success"},
    )
    def patch(self, request, store_id=None):
        store = get_object_or_404(StoreModel, id=store_id)
        data = {}
        try:
            for k, v in request.data.items():
                if v:
                    data[k] = v
        except Exception as e:
            return Response(
                {"message": 'A problem has occurred.'}, status=status.HTTP_400_BAD_REQUEST
            )
        if request.data.get("store_name"):
            return Response(
                {"message": "The store name cannot be changed."}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UpdateStoreSerializer(store, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Store information has been modified."}, status=status.HTTP_200_OK)
        return Response(
            {"message": str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST
        )


class GoodsPatchView(APIView):
    # permission_classes = [IsSeller]

    @swagger_auto_schema(
        tags=["Multiple product modifications"],
        request_body=PostSerializer,
        responses={200: "Success"},
    )
    def patch(self, request):
        if request.data.get('goods_set'):
            for data in request.data.get("goods_set"):
                if data:
                    data = data.copy()
                    if 'Kip' in data['price']:
                        data['price'] = data['price'][:-1]
                    goods = get_object_or_404(GoodsModel, id=data.get("id"))
                    serializer = GoodsSerializer(goods, data=data, partial=True)
                    category, is_created = CategoryModel.objects.get_or_create(name=data.get('category'))
                    if serializer.is_valid():
                        instance = serializer.save(category=category)
                        images_data = data.get('images', [])
                        if images_data:
                            instance.imagemodel_set.all().delete()
                            for idx, image_data in enumerate(images_data):
                                # Convert Base64 encoded string to image file
                                # Delete all existing images and save as new -> It would be better to select the image and edit it later.
                                format, imgstr = image_data.split(';base64,')
                                ext = format.split('/')[-1]
                                file_data = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
                                # Create a new image object and save it with the image file
                                ImageModel.objects.create(goods=instance, image=file_data)
                    else:
                        print(serializer.errors)
            return Response({"message": "The product has been modified."}, status=status.HTTP_200_OK)
        return Response({"message": "A problem has occurred."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if request.data.get('goods_id'):
            goods = get_object_or_404(GoodsModel, id=request.data.get("goods_id"))
            goods.delete()
        return Response({"message": "success"}, status=status.HTTP_200_OK)


class ReviewView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    """
     <Logic related to reviews>
     Edit and delete review -> pk = id of review
     """

    @swagger_auto_schema(tags=["View and write product reviews"], responses={200: "Success"})
    def get(self, request, pk):
        # pk = product id
        review = ReviewModel.objects.filter(goods_id=pk).order_by("-created_at")
        serializer = ReviewSerializer(review, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["View and write product reviews"], request_body=PostSerializer, responses={201: "Created"}
    )
    def post(self, request, pk):
        # pk = product id
        review = ReviewModel.objects.filter(user=request.user, goods_id=pk).exists()
        order = OrderModel.objects.filter(user=request.user, goods_id=pk).exists()
        if not order:
            return Response({"message": "Only users who have placed an order can leave a review."}, status=status.HTTP_400_BAD_REQUEST)
        if review:
            return Response({"message": "I've already written a review."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(goods_id=pk, user=request.user)
            return Response({"message": "Review completed"}, status=status.HTTP_201_CREATED)
        return Response({"message": "Please use after logging in."}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        review = get_object_or_404(ReviewModel, id=pk, user=request.user)
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        review = get_object_or_404(ReviewModel, id=pk, user=request.user)
        review.delete()
        return Response({"message": "success"}, status=status.HTTP_200_OK)


class CheckReview(APIView):
    def post(self, request, pk):
        review = ReviewModel.objects.filter(user=request.user, goods_id=pk).exists()
        order = OrderModel.objects.filter(user=request.user, goods_id=pk).exists()
        if not order:
            return Response({"message": "Only users who have placed an order can leave a review."}, status=status.HTTP_400_BAD_REQUEST)
        if review:
            return Response({"message": "I've already written a review."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "success"}, status=status.HTTP_200_OK)


class TermsAPI(APIView):
    def get(self, request, pk):
        # 1: Terms of Use, 2: Privacy Policy
        turm = PolicyModel.objects.filter(category=pk).last()
        content = turm.content if turm else ""
        return Response({"content": content}, status=status.HTTP_200_OK)


def review_form(request, pk):
    form = ReviewForm()
    return render(request, 'store/review.html', {'form': form, "goods_id": pk})


def review_list(request, pk):
    return render(request, 'store/review_list.html', {"goods_id": pk})


# class OrderView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#     """
#     <Product order logic>
#     """

#     @swagger_auto_schema(tags=["Product ordering and inquiry"], responses={200: "Success"})
#     def get(self, request):
#         order_set = (
#             OrderModel.objects.filter(user=request.user).distinct().values("goods")
#         )
#         data = []
#         if order_set:
#             for order in order_set:
#                 goods = GoodsModel.objects.get(id=order['goods'])
#                 data.append(GoodsSerializer(goods).data)
#             return Response(data, status=status.HTTP_200_OK)
#         return Response([], status=status.HTTP_200_OK)

#     @swagger_auto_schema(
#         tags=["Product ordering and inquiry"], request_body=PostSerializer, responses={200: "Success"}
#     )
#     def post(self, request):
#         goods_id = request.data.get("goods_id")

#         goods = get_object_or_404(GoodsModel, id=goods_id)
#         goods = GoodsSerializer(goods).data.copy()

#         serializer = OrderSerializer(data=goods)

#         if serializer.is_valid(raise_exception=True):
#             try:
#                 serializer.save(user=request.user, goods_id=goods_id)
#                 return Response({"message": "I ordered a product."}, status=status.HTTP_200_OK)
#             except Exception as e:
#                 return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SearchView(APIView):
    @swagger_auto_schema(
        tags=["search"], request_body=PostSerializer, responses={200: "Success"}
    )
    def post(self, request):
        search_word = request.data.get("search")
        goods_set = GoodsModel.objects.filter(
            Q(name__icontains=search_word) | Q(store__name__icontains=search_word)
        )

        goods = GoodsSerializer(goods_set, many=True).data

        return Response(goods, status=status.HTTP_200_OK)


def resize_image(image_data, output_size=(800, 600), quality=85):
    """
     Adjust the resolution of the image file and save it in JPEG format.
     :param image_data: Original image data (base64 encoded string).
     :param output_size: Size (width, height) of the image to be changed.
     :param quality: JPEG storage quality (1-100).
     :return: Changed image data (base64 encoded string).
     """
    # Convert image data to PIL image object
    image = Image.open(io.BytesIO(base64.b64decode(image_data)))

    # Change image size
    image = image.resize(output_size, Image.ANTIALIAS)

    # Save in JPEG format
    output_buffer = io.BytesIO()
    image.save(output_buffer, format='JPEG', quality=quality)
    output_data = base64.b64encode(output_buffer.getvalue()).decode()

    return output_data


# Cart
class CartListView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

class CartDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

class UserCartListView(generics.ListAPIView):
    serializer_class = CartSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Cart.objects.filter(user_id=user_id)

class CartCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CreateCartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "success"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartUpdateAPIView(APIView):
    def put(self, request, pk):
        try:
            cart = Cart.objects.get(pk=pk)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CartUpdateSerializer(cart, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartDeleteView(generics.DestroyAPIView):
    def delete(self, request, pk, format=None):
        try:
            cart = Cart.objects.get(pk=pk)
        except Cart.DoesNotExist:
            return Response({"message": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Delete related CartItem instances
        CartItem.objects.filter(cart_id=cart).delete()

        # Delete the Cart instance
        cart.delete()

        return Response({"message": "success"}, status=status.HTTP_204_NO_CONTENT)

class CartItemDeleteView(generics.DestroyAPIView):
    def delete(self, request, pk, format=None):
        try:
            cartItme = CartItem.objects.get(pk=pk)
        except CartItem.DoesNotExist:
            return Response({"message": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        # Delete the Cart instance
        cartItme.delete()

        return Response({"message": "success"}, status=status.HTTP_204_NO_CONTENT)


# # Order
# class OrderListView(generics.ListCreateAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer

#     def get_queryset(self):
#         # Retrieve orders with status "Pending"
#         return Order.objects.filter(status="Pending")
    
# class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
    
# class UserOrderListView(generics.ListAPIView):
#     serializer_class = OrderSerializer

#     def get_queryset(self):
#         user_id = self.kwargs['user_id']
#         return Order.objects.filter(user_id=user_id)
    
# class OrderCreateAPIView(APIView):
#     def post(self, request):
#         serializer = OrderCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "success"},status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# class PendingOrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.filter(status='Pending')
#     serializer_class = PendingOrderSerializer

# New one
# Order
class OrderListView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Retrieve orders with status "Pending"
        return Order.objects.filter(status="Pending")

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class UserOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Order.objects.filter(user_id=user_id)
    

# class CreateOrderView(generics.CreateAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer


class OrderCreateAPIView(APIView):
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "success"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class OrderUpdateAPIView(APIView):
    def put(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrderUpdateSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class OrderDeleteView(generics.DestroyAPIView):
    def delete(self, request, pk, format=None):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Delete related OrderItem instances
        OrderItem.objects.filter(order_id=order).delete()

        # Delete the Order instance
        order.delete()

        return Response({"message": "success"}, status=status.HTTP_204_NO_CONTENT)
    
# class PendingOrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.filter(status='Pending')
#     serializer_class = PendingOrderSerializer

# class ProcessingOrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.filter(status='Processing')
#     serializer_class = ProcessingOrderSerializer

# class ShippedOrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.filter(status='Shipped')
#     serializer_class = ShippedOrderSerializer

# class DeliveredOrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.filter(status='Delivered')
#     serializer_class = DeliveredOrderSerializer

# # ################ Example for get pending order by store is ################
# class PendingOrderListAPIView(generics.ListAPIView):
#     serializer_class = PendingOrderSerializer

#     def get_queryset(self):
#         store_id = self.request.query_params.get('store_id', None)
#         if store_id is not None:
#             return Order.objects.filter(status='Pending', store_id=store_id)
#         else:
#             return Order.objects.filter(status='Pending')

class PendingOrderListAPIView(generics.ListAPIView):
    serializer_class = PendingOrderSerializer

    def get_queryset(self):
        return Order.objects.filter(status='Pending')
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        count = queryset.count()
        serializer = self.serializer_class(queryset, many=True)
        return Response({
            'count': count,
            'orders': serializer.data
        })

class ProcessingOrderListAPIView(generics.ListAPIView):
    serializer_class = ProcessingOrderSerializer

    def get_queryset(self):
        return Order.objects.filter(status='Processing')
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        count = queryset.count()
        serializer = self.serializer_class(queryset, many=True)
        return Response({
            'count': count,
            'orders': serializer.data
        })

class ShippedOrderListAPIView(generics.ListAPIView):
    serializer_class = ShippedOrderSerializer

    def get_queryset(self):
        return Order.objects.filter(status='Shipped')
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        count = queryset.count()
        serializer = self.serializer_class(queryset, many=True)
        return Response({
            'count': count,
            'orders': serializer.data
        })
    
class DeliveredOrderListAPIView(generics.ListAPIView):
    serializer_class = DeliveredOrderSerializer

    def get_queryset(self):
        return Order.objects.filter(status='Delivered')
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        count = queryset.count()
        serializer = self.serializer_class(queryset, many=True)
        return Response({
            'count': count,
            'orders': serializer.data
        })

# Good edit
class GoodsEditAPIView(generics.UpdateAPIView):
    queryset = GoodsModel.objects.all()
    serializer_class = GoodsEditSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
class GoodsImageEditAPIView(generics.UpdateAPIView):
    queryset = ImageModel.objects.all()
    serializer_class = ImageSerializer
    lookup_field = 'goods'

    def update(self, request, *args, **kwargs):
        goods_id = kwargs.get('pk')
        try:
            image_instance = ImageModel.objects.get(goods_id=goods_id)
        except ImageModel.DoesNotExist:
            return Response({'detail': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(image_instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
