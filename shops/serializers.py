# shops/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import CoffeeShop, Queue, Profile, PushSubscription
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# --- Serializer untuk Otentikasi ---
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        if hasattr(user, 'profile'):
            token['role'] = user.profile.role
            if user.profile.coffee_shop:
                token['shop_id'] = user.profile.coffee_shop.id
        return token

# --- Serializer untuk Model Utama ---
class CoffeeShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoffeeShop
        fields = ['id', 'owner', 'name', 'address', 'logo', 'plan']

class QueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Queue
        fields = ['id', 'coffee_shop', 'queue_number', 'status', 'created_at', 'updated_at']
        read_only_fields = ['coffee_shop', 'queue_number']

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        return user

# --- PERBAIKAN FINAL ADA DI SINI ---
# --- GANTI SELURUH CLASS INI ---
class PushSubscriptionSerializer(serializers.Serializer):
    """
    Serializer ini hanya untuk memvalidasi data JSON yang masuk dari frontend.
    """
    subscription_info = serializers.JSONField()

    class Meta:
        # Kita tidak menghubungkannya ke model secara langsung
        # karena kita akan menangani penyimpanan secara manual.
        pass
