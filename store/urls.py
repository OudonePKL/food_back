from django.conf.urls.static import static
from django.urls import path
from django.conf import settings
from store import views


urlpatterns = [
    path("", views.GoodsView.as_view(), name="goods_list"),  # Product list related
    path("detail/<int:goods_id>", views.GoodsView.as_view(), name="goods_detail"),  # Product list related
    path("<int:store_id>", views.StoreView.as_view(), name="store"),  # Store Related Related
    path(
        "goods", views.GoodsPatchView.as_view(), name="goods_change"
    ),  # Related to modifying goods -> Placement of different views due to permission settings
    path(
        "goods/<int:goods_id>", views.GoodsView.as_view(), name="goods_detail"
    ),  # Product related
    path("review/<int:pk>", views.ReviewView.as_view(), name="review"),  # Review related
    # Cart
    path('carts', views.CartListView.as_view(), name='cart-list'),
    path('cart/<int:pk>', views.CartDetailView.as_view(), name='cart-detail'),
    path('user/<int:user_id>/cart', views.UserCartListView.as_view(), name='user-cart-list'),
    path('cart/create', views.CartCreateAPIView.as_view(), name='create_cart'),
    path('cart/update/<int:pk>', views.CartUpdateAPIView.as_view(), name='cart-update'),
    path('cart/delete/<int:pk>', views.CartDeleteView.as_view(), name='delete-cart'),
    path('cart/item/delete/<int:pk>', views.CartItemDeleteView.as_view(), name='delete-cart-item'),
    # path("order", views.OrderView.as_view(), name="order"),  # Order related
    # new order
    path('orders', views.OrderListView.as_view(), name='order-list'),
    path('order/create', views.OrderCreateAPIView.as_view(), name='order-create'),
    path('order/update/<int:pk>', views.OrderUpdateAPIView.as_view(), name='order-update'),
    path('order/<int:pk>', views.OrderDetailView.as_view(), name='order-detail'),
    path('user/<int:user_id>/order', views.UserOrderListView.as_view(), name='user-order-list'),
    path('order/delete/<int:pk>', views.OrderDeleteView.as_view(), name='delete-order'),
    path('order/pending/', views.PendingOrderListAPIView.as_view(), name='pending-orders'),
    path('order/processing/', views.ProcessingOrderListAPIView.as_view(), name='processing-orders'),
    path('order/shipped/', views.ShippedOrderListAPIView.as_view(), name='shipped-orders'),
    path('order/delivered/', views.DeliveredOrderListAPIView.as_view(), name='delivered-orders'),
    path("search", views.SearchView.as_view(), name="search"),  # Order related
    path("check-review/<int:pk>", views.CheckReview.as_view(), name="CheckReview"),  # Order related
    path("terms/<int:pk>", views.TermsAPI.as_view(), name="terms"),  # Order related
    # Template render only
    path("review/form/<int:pk>", views.review_form, name="review_form"),
    path("review/list/<int:pk>", views.review_list, name="review_list"),
    path('products/<int:pk>/reviews/', views.ReviewView.as_view(), name='product_reviews'),
    path("goods/list", views.goods_list, name="goods_list"),
    path("goods/detail/<int:goods_id>", views.goods_detail, name="goods_detail"),
    path('goods/<int:pk>/edit/', views.GoodsEditAPIView.as_view(), name='goods-edit'),
    path('goods/image/<int:pk>/edit/', views.GoodsImageEditAPIView.as_view(), name='goods-image-edit'),
    path("order/list", views.order_list, name="order_list"),
    path("setting", views.store_setting, name="store_setting"),
]
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
