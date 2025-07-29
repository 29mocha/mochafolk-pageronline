# shops/views.py

from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from django.db.models import Count, Avg, F
from django.db.models.functions import TruncDate, ExtractHour
from django.http import HttpResponse

# Imports for Password Reset
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail

from rest_framework import generics, status, permissions, views
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import CoffeeShop, Queue, Profile, PushSubscription
from .serializers import (
    CoffeeShopSerializer, 
    QueueSerializer, 
    UserSerializer, 
    MyTokenObtainPairSerializer,
    PushSubscriptionSerializer
)
from .permissions import IsOwner, IsShopMember

import xendit
import midtransclient
import uuid
import qrcode
import io
import json
from pywebpush import webpush # <-- Impor untuk webpush
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from cryptography.hazmat.primitives import serialization
import base64
# --- Authentication Views ---

class MyTokenObtainPairView(generics.GenericAPIView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        shop_name = f"{user.username}'s Coffee Shop"
        new_shop = CoffeeShop.objects.create(name=shop_name, owner=user, plan=CoffeeShop.Plan.BASIC)
        
        user.profile.role = Profile.Role.OWNER
        user.profile.coffee_shop = new_shop
        user.profile.save()
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# --- Password Reset Views ---

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'If an account with this email exists, a password reset link has been sent.'}, status=status.HTTP_200_OK)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

        send_mail(
            'Password Reset for MochaFolk',
            f'Please click the link to reset your password: {reset_link}',
            'noreply@mochafolk.com',
            [user.email],
            fail_silently=False,
        )

        return Response({'message': 'If an account with this email exists, a password reset link has been sent.'}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        password = request.data.get('password')

        if not all([uidb64, token, password]):
            return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(password)
            user.save()
            return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid token or user.'}, status=status.HTTP_400_BAD_REQUEST)

# --- Shop and Queue Management Views ---

class CoffeeShopListCreateView(generics.ListCreateAPIView):
    queryset = CoffeeShop.objects.all()
    serializer_class = CoffeeShopSerializer
    permission_classes = [IsAuthenticated]


class CoffeeShopDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CoffeeShop.objects.all()
    serializer_class = CoffeeShopSerializer

    def get_permissions(self):
        """
        Izinkan siapa saja untuk melihat detail (GET),
        tetapi hanya Owner untuk mengubahnya (PUT, PATCH, DELETE).
        """
        if self.request.method == 'GET':
            # Siapa saja boleh melihat nama, logo, dll.
            return [permissions.AllowAny()]
        # Untuk mengubah data toko, harus Owner
        return [permissions.IsAuthenticated(), IsOwner()]

class QueueListCreateView(generics.ListCreateAPIView):
    serializer_class = QueueSerializer

    def get_queryset(self):
        shop_id = self.kwargs['shop_pk']
        today = timezone.localdate()
        return Queue.objects.filter(
            coffee_shop_id=shop_id,
            created_at__date=today
        )

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsShopMember()]
    
    def perform_create(self, serializer):
        shop_id = self.kwargs.get('shop_pk')
        shop = CoffeeShop.objects.get(pk=shop_id)
        
        # Periksa batasan untuk paket BASIC
        if shop.plan == CoffeeShop.Plan.BASIC:
            today = timezone.localdate()
            todays_queues_count = Queue.objects.filter(
                coffee_shop_id=shop_id, 
                created_at__date=today
            ).count()
            
            if todays_queues_count >= 20:
                raise ValidationError("Batas 20 antrian harian untuk paket Basic telah tercapai.")

        # Lanjutkan dengan logika pembuatan nomor dan penyimpanan
        today = timezone.localdate()
        new_queue_number = Queue.objects.filter(coffee_shop_id=shop_id, created_at__date=today).count() + 1
        
        instance = serializer.save(coffee_shop=shop, queue_number=new_queue_number)
        
        # Kirim notifikasi WebSocket
        try:
            channel_layer = get_channel_layer()
            group_name = f"queue_shop_{shop_id}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "queue.new",
                    "message": QueueSerializer(instance).data
                }
            )
        except Exception as e:
            print(f"Peringatan: Gagal mengirim notifikasi WebSocket (antrian baru): {e}")

class QueueDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QueueSerializer
    lookup_url_kwarg = 'queue_pk'
    def get_queryset(self):
        shop_id = self.kwargs['shop_pk']
        return Queue.objects.filter(coffee_shop_id=shop_id)
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsShopMember()]
    def perform_update(self, serializer):
        instance = serializer.save()
        
        if instance.status == 'ready':
            # --- KUNCI PERBAIKAN: Tambahkan try-except ---
            try:
                # Kirim notifikasi WebSocket
                channel_layer = get_channel_layer()
                group_name = f"queue_shop_{instance.coffee_shop.id}"
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        "type": "queue.update",
                        "message": { "id": instance.id, "queue_number": instance.queue_number, "status": instance.status }
                    }
                )

                # Kirim Push Notification
                subscriptions = PushSubscription.objects.filter(coffee_shop_id=instance.coffee_shop.id)
                payload = json.dumps({
                    "title": f"Pesanan #{instance.queue_number} Siap!",
                    "body": f"Pesanan Anda di {instance.coffee_shop.name} sudah siap diambil.",
                    "url": f"/queue/{instance.coffee_shop.id}"
                })
                for sub in subscriptions:
                    try:
                        subscription_info_dict = {
                            "endpoint": sub.endpoint,
                            "keys": { "p256dh": sub.p256dh, "auth": sub.auth }
                        }
                        webpush(
                            subscription_info=subscription_info_dict,
                            data=payload,
                            vapid_private_key=settings.VAPID_PRIVATE_KEY,
                            vapid_claims=settings.WEBPUSH_CLAIMS
                        )
                    except Exception as e:
                        # Jika langganan spesifik gagal, hapus dari DB
                        if 'Gone' in str(e):
                            print(f"Langganan {sub.endpoint} sudah tidak valid. Menghapus.")
                            sub.delete()
                        else:
                            print(f"Gagal mengirim push notification ke {sub.endpoint}: {e}")

            except Exception as e:
                print(f"Peringatan: Gagal mengirim notifikasi (update status): {e}")

class ResetQueueView(APIView):
    permission_classes = [IsAuthenticated, IsShopMember]
    def post(self, request, shop_pk=None):
        queues_to_reset = Queue.objects.filter(
            coffee_shop_id=shop_pk,
            status__in=['waiting', 'ready']
        )
        count = queues_to_reset.update(status='done')
        return Response({'message': f'{count} antrian telah direset.'}, status=status.HTTP_200_OK)

class RingPagerView(APIView):
    permission_classes = [IsAuthenticated, IsShopMember]
    def post(self, request, shop_pk=None, queue_pk=None):
        try:
            queue = Queue.objects.get(pk=queue_pk, coffee_shop_id=shop_pk)
            channel_layer = get_channel_layer()
            group_name = f"queue_shop_{shop_pk}"
            async_to_sync(channel_layer.group_send)(group_name, { "type": "pager.ring", "message": { "id": queue.id } })
            
            subscriptions = PushSubscription.objects.filter(coffee_shop_id=shop_pk)
            payload = json.dumps({
                "title": f"Pager untuk Pesanan #{queue.queue_number}",
                "body": f"Silakan ambil pesanan Anda di {queue.coffee_shop.name} sekarang.",
                "url": f"/queue/{queue.coffee_shop.id}" # <-- KUNCI PERBAIKAN
            })
            for sub in subscriptions:
                try:
                    subscription_info_dict = {
                        "endpoint": sub.endpoint,
                        "keys": { "p256dh": sub.p256dh, "auth": sub.auth }
                    }
                    webpush(
                        subscription_info=subscription_info_dict,
                        data=payload,
                        vapid_private_key=settings.VAPID_PRIVATE_KEY,
                        vapid_claims=settings.WEBPUSH_CLAIMS
                    )
                except Exception as e:
                    # --- 3. HAPUS LANGGANAN YANG TIDAK VALID (ERROR 410) ---
                    if '410 Gone' in str(e):
                        print(f"Langganan {sub.endpoint} sudah tidak valid. Menghapus.")
                        sub.delete()
                    else:
                        print(f"Gagal mengirim push notification ke {sub.endpoint}: {e}")

            return Response({"status": "pager signals sent"}, status=status.HTTP_200_OK)

        except Queue.DoesNotExist:
            return Response({"error": "Queue not found"}, status=status.HTTP_404_NOT_FOUND)



class QRCodeView(APIView):
    # Izinkan akses publik agar gambar bisa dimuat di browser
    permission_classes = [AllowAny] 

    def get(self, request, shop_pk=None):
        # URL frontend yang akan dibuka saat QR code di-scan
        # Nanti saat deploy, ganti 'http://localhost:3000' dengan domain Anda
        frontend_url = f"http://localhost:3000/queue/{shop_pk}"
        
        # Buat gambar QR code di memori
        img = qrcode.make(frontend_url)
        
        # Simpan gambar ke buffer byte
        buf = io.BytesIO()
        img.save(buf, 'PNG')
        buf.seek(0)
        
        # Kembalikan sebagai respons HTTP dengan tipe konten gambar
        return HttpResponse(buf, content_type='image/png')

# --- Owner Specific Views ---

class MyCoffeeShopView(generics.RetrieveUpdateAPIView):
    serializer_class = CoffeeShopSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    def get_object(self):
        return CoffeeShop.objects.get(owner=self.request.user)

class AddStaffView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    def perform_create(self, serializer):
        staff_user = serializer.save()
        owner_profile = self.request.user.profile
        staff_user.profile.role = Profile.Role.STAFF
        staff_user.profile.coffee_shop = owner_profile.coffee_shop
        staff_user.profile.save()

class StaffListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    def get_queryset(self):
        owner_shop = self.request.user.profile.coffee_shop
        if not owner_shop:
            return User.objects.none()
        return User.objects.filter(
            profile__coffee_shop=owner_shop,
            profile__role=Profile.Role.STAFF
        )

class DeleteStaffView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    def get_queryset(self):
        owner_shop = self.request.user.profile.coffee_shop
        if not owner_shop:
            return User.objects.none()
        return User.objects.filter(
            profile__coffee_shop=owner_shop,
            profile__role=Profile.Role.STAFF
        )

# --- Analytics Views ---

class DailyQueueCountView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]
    def get(self, request, *args, **kwargs):
        owner_shop = request.user.profile.coffee_shop
        if not owner_shop:
            return Response({"detail": "User does not have an associated coffee shop."}, status=status.HTTP_400_BAD_REQUEST)
        today = timezone.localdate()
        start_date = today - timedelta(days=6)
        daily_counts = owner_shop.queues.filter(
            created_at__date__gte=start_date
        ).annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
        counts_by_date = {item['date'].strftime('%Y-%m-%d'): item['count'] for item in daily_counts}
        response_data = []
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            date_key = current_date.strftime('%Y-%m-%d')
            response_data.append({'date': date_key, 'count': counts_by_date.get(date_key, 0)})
        return Response(response_data)

class PeakHoursView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]
    def get(self, request, *args, **kwargs):
        owner_shop = request.user.profile.coffee_shop
        if not owner_shop:
            return Response({"detail": "User does not have an associated coffee shop."}, status=status.HTTP_400_BAD_REQUEST)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        hourly_counts = Queue.objects.filter(
            coffee_shop=owner_shop,
            created_at__date__gte=thirty_days_ago
        ).annotate(hour=ExtractHour('created_at')).values('hour').annotate(count=Count('id')).order_by('hour')
        response_data = [0] * 24
        for item in hourly_counts:
            response_data[item['hour']] = item['count']
        return Response(response_data)

class AverageWaitTimeView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]
    def get(self, request, *args, **kwargs):
        owner_shop = request.user.profile.coffee_shop
        if not owner_shop:
            return Response({"detail": "User does not have an associated coffee shop."}, status=status.HTTP_400_BAD_REQUEST)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        average_wait_time = Queue.objects.filter(
            coffee_shop=owner_shop,
            created_at__date__gte=thirty_days_ago,
            status__in=['ready', 'done']
        ).annotate(wait_time=F('updated_at') - F('created_at')).aggregate(avg_wait=Avg('wait_time'))
        avg_seconds = 0
        if average_wait_time['avg_wait']:
            avg_seconds = average_wait_time['avg_wait'].total_seconds()
        return Response({'average_wait_seconds': avg_seconds})

# --- Payment Views ---

class CreateMidtransTransactionView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]
    def post(self, request, *args, **kwargs):
        snap = midtransclient.Snap(
            is_production=settings.MIDTRANS_IS_PRODUCTION,
            server_key=settings.MIDTRANS_SERVER_KEY,
        )
        user = request.user
        owner_shop = user.profile.coffee_shop
        if owner_shop.plan == 'PRO':
            return Response({'message': 'Anda sudah berada di paket Pro.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order_id = f"MF-PRO-{owner_shop.id}-{int(timezone.now().timestamp())}"
            customer_email = user.email if user.email else f"{user.username}@mochafolk.app"
            transaction_params = {
                "transaction_details": { "order_id": order_id, "gross_amount": 55000 },
                "customer_details": { "first_name": user.username, "email": customer_email },
            }
            transaction = snap.create_transaction(transaction_params)
            payment_url = transaction['redirect_url']
            return Response({'payment_url': payment_url})
        except Exception as e:
            print(f"!! ERROR DARI MIDTRANS: {e} !!") 
            return Response({'error': 'Gagal berkomunikasi dengan Midtrans.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MidtransWebhookView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        data = request.data
        print("--- Webhook Midtrans Diterima ---")
        print(data)
        order_id = data.get('order_id')
        transaction_status = data.get('transaction_status')
        fraud_status = data.get('fraud_status')
        if transaction_status in ['settlement', 'capture'] and fraud_status == 'accept':
            try:
                shop_id_str = order_id.split('-')[2]
                shop_id = int(shop_id_str)
                with transaction.atomic():
                    shop = CoffeeShop.objects.select_for_update().get(pk=shop_id)
                    if shop.plan == 'BASIC':
                        shop.plan = CoffeeShop.Plan.PRO
                        shop.save()
                        print(f"SUKSES: Paket untuk toko ID {shop_id} telah di-upgrade ke PRO.")
                    else:
                        print(f"INFO: Paket untuk toko ID {shop_id} sudah PRO.")
            except Exception as e:
                print(f"ERROR saat memproses webhook Midtrans: {e}")
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            print(f"INFO: Transaksi {order_id} diabaikan (status: {transaction_status})")
        return Response(status=status.HTTP_200_OK)
class SavePushSubscriptionView(generics.GenericAPIView):
    serializer_class = PushSubscriptionSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        subscription_info = serializer.validated_data.get('subscription_info')
        shop_id = self.kwargs.get('shop_pk')
        coffee_shop = CoffeeShop.objects.get(pk=shop_id)
        
        endpoint = subscription_info.get('endpoint')
        p256dh = subscription_info.get('keys', {}).get('p256dh')
        auth = subscription_info.get('keys', {}).get('auth')
        
        if not all([endpoint, p256dh, auth]):
            return Response({'error': 'Data langganan tidak lengkap.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or update the subscription
        PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                'coffee_shop': coffee_shop,
                'p256dh': p256dh,
                'auth': auth,
                # The line causing the error has been removed.
            }
        )
        
        return Response(status=status.HTTP_201_CREATED)
        
class VapidPublicKeyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # Ambil kunci PEM dari settings
        pem_public_key = settings.VAPID_PUBLIC_KEY

        try:
            # --- PERBAIKAN: Bersihkan kunci sebelum diproses ---
            clean_pem_key = pem_public_key.replace(
                '-----BEGIN PUBLIC KEY-----', ''
            ).replace(
                '-----END PUBLIC KEY-----', ''
            ).replace(
                '\n', ''
            ).strip()
            
            # Buat ulang format PEM yang benar
            full_pem_key = (
                "-----BEGIN PUBLIC KEY-----\n"
                + clean_pem_key
                + "\n-----END PUBLIC KEY-----"
            )

            public_key_obj = serialization.load_pem_public_key(
                full_pem_key.encode("utf-8")
            )

            raw_public_key = public_key_obj.public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint
            )

            url_safe_base64_public_key = base64.urlsafe_b64encode(raw_public_key).rstrip(b'=').decode('utf-8')

            return Response({'public_key': url_safe_base64_public_key})
        
        except Exception as e:
            print(f"ERROR saat memproses VAPID key: {e}")
            return Response({'error': 'Gagal memproses kunci VAPID.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)