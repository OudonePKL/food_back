from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from store import views
from rest_framework.routers import DefaultRouter
from .views import BankAccountViewSet

router = DefaultRouter()
router.register(r'bank-accounts/detail', BankAccountViewSet)


urlpatterns = [
    path("categories", views.CategoryListCreate.as_view(), name='category-list-create'),
    path("", views.GoodsView.as_view(), name="goods_list"),  # Product list related
    path("detail/<int:goods_id>", views.GoodsView.as_view(), name="goods_detail"),  # Product list related
    path("<int:store_id>", views.CreateProductAPIView.as_view(), name="store"),  # Store Related Related
    path('product/create', views.CreateProductAPIView.as_view(), name='create-product'),
    path('product/update/<int:pk>', views.UpdateProductAPIView.as_view(), name='update-product'),
    path('product/delete/<int:pk>', views.DeleteProductAPIView.as_view(), name='delete-product'),
    path(
        "goods", views.GoodsPatchView.as_view(), name="goods_change"
    ),  # Related to modifying goods -> Placement of different views due to permission settings
    path(
        "goods/<int:goods_id>", views.GoodsView.as_view(), name="goods_detail"
    ),  # Product related
    path("review/<int:pk>", views.ReviewView.as_view(), name="review"),  # Review related
    
    # old order
    path("order", views.OrderView.as_view(), name="order"),  # Order related
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
    # # Review
    path('reviews', views.ReviewList.as_view(), name='review-list'),
    path('review/create', views.ReviewCreate.as_view(), name='review-create'),
    path('review/<int:pk>', views.ReviewRetrieveUpdateDestroy.as_view(), name='review-detail'),
    # path('review/update/<int:pk>', views.ReviewRetrieveUpdateDestroy.as_view(), name='review-update'),
    # path('user/<int:user_id>/review', views.UserReviewListView.as_view(), name='user-reviews-list'),
    path('product/<int:product_id>/review', views.ProductReviewListView.as_view(), name='product-reviews-list'),
    # path('review/delete/<int:pk>', views.ReviewDeleteView.as_view(), name='delete-reviews'),

    path("goods/list", views.goods_list, name="goods_list"),
    path("goods/detail/<int:goods_id>", views.goods_detail, name="goods_detail"),
    path("order/list", views.order_list, name="order_list"),
    path("setting", views.store_setting, name="store_setting"),
    # bank account
    path('bank-accounts', views.BankAccountListCreateAPIView.as_view(), name='bank-account-list-create'),
    path('bank-accounts/<int:pk>', views.BankAccountRetrieveUpdateDestroyAPIView.as_view(), name='bank-account-detail'),
    path('bank-accounts/<int:store_id>/has_bank_account', views.check_store_bank_account, name='check_store_bank_account'),
    path('', include(router.urls)),
    path('bank-accounts/update/<int:store_id>', views.BankAccountUpdateAPIView.as_view(), name='bank-account-update'),
]
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
