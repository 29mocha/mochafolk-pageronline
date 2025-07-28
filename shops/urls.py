# shops/urls.py
from django.urls import path
from .views import (
    # Views untuk Pelanggan & Barista
    CoffeeShopListCreateView, 
    CoffeeShopDetailView,
    QueueListCreateView,
    QueueDetailView,
    ResetQueueView,
    RingPagerView,
    QRCodeView,
    SavePushSubscriptionView,
    VapidPublicKeyView,
    
    # Views untuk Owner
    MyCoffeeShopView,
    AddStaffView,
    StaffListView,
    DeleteStaffView,
    CreateMidtransTransactionView,

    # Views untuk Analitik
    DailyQueueCountView,
    PeakHoursView,
    AverageWaitTimeView
)

urlpatterns = [
    # --- URL Publik & Dasbor Barista ---
    path('', CoffeeShopListCreateView.as_view(), name='coffeeshop-list-create'),
    path('<int:pk>/', CoffeeShopDetailView.as_view(), name='coffeeshop-detail'),
    path('<int:shop_pk>/queues/', QueueListCreateView.as_view(), name='queue-list-create'),
    path('<int:shop_pk>/queues/<int:queue_pk>/', QueueDetailView.as_view(), name='queue-detail'),
    path('<int:shop_pk>/queues/<int:queue_pk>/ring/', RingPagerView.as_view(), name='pager-ring'),
    path('<int:shop_pk>/reset-queue/', ResetQueueView.as_view(), name='reset-queue'),
    path('<int:shop_pk>/qr-code/', QRCodeView.as_view(), name='shop-qr-code'),
    # URL untuk menyimpan langganan notifikasi
    path('<int:shop_pk>/save-subscription/', SavePushSubscriptionView.as_view(), name='save-push-subscription'),
    path('vapid-public-key/', VapidPublicKeyView.as_view(), name='vapid-public-key'),
    # --- URL Khusus untuk Pemilik Toko yang Sedang Login ---
    path('my-shop/', MyCoffeeShopView.as_view(), name='my-coffeeshop'),
    path('my-shop/add-staff/', AddStaffView.as_view(), name='add-staff'),
    path('my-shop/staff/', StaffListView.as_view(), name='list-staff'),
    path('my-shop/staff/<int:pk>/delete/', DeleteStaffView.as_view(), name='delete-staff'),
    path('my-shop/upgrade-midtrans/', CreateMidtransTransactionView.as_view(), name='create-midtrans-transaction'),
    
    # --- URL untuk Analitik ---
    path('my-shop/analytics/daily-counts/', DailyQueueCountView.as_view(), name='analytics-daily-counts'),
    path('my-shop/analytics/peak-hours/', PeakHoursView.as_view(), name='analytics-peak-hours'),
    path('my-shop/analytics/avg-wait-time/', AverageWaitTimeView.as_view(), name='analytics-avg-wait-time'),
]
