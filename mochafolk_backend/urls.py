# mochafolk_backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from shops.views import MidtransWebhookView

# Import view dari simplejwt dan view registrasi kita
from rest_framework_simplejwt.views import TokenRefreshView
from shops.views import RegisterView, MyTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/shops/', include('shops.urls')),
    
    # URL untuk otentikasi
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/webhooks/midtrans/', MidtransWebhookView.as_view(), name='midtrans-webhook'),
    
    # URL untuk webhook akan kita tambahkan nanti untuk Midtrans
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)