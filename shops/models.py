# shops/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# --- Model Profile Baru ---
class Profile(models.Model):
    class Role(models.TextChoices):
        OWNER = 'OWNER', 'Owner'
        STAFF = 'STAFF', 'Staff'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=5, choices=Role.choices, default=Role.STAFF)
    # Setiap profile terhubung ke satu coffee shop
    coffee_shop = models.ForeignKey('CoffeeShop', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role} at {self.coffee_shop.name if self.coffee_shop else 'No Shop'}"

class CoffeeShop(models.Model):
    # --- BARU: Definisikan pilihan paket ---
    class Plan(models.TextChoices):
        BASIC = 'BASIC', 'Basic'
        PRO = 'PRO', 'Pro'

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coffee_shops', null=True)
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    plan = models.CharField(max_length=5, choices=Plan.choices, default=Plan.BASIC)
    
    SUBSCRIPTION_CHOICES = [
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    subscription_status = models.CharField(max_length=10, choices=SUBSCRIPTION_CHOICES, default='trial')
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

# --- Tambahkan Model Baru Di Sini ---
class Queue(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('ready', 'Ready'),
        ('done', 'Done'),
    ]
    
    coffee_shop = models.ForeignKey(CoffeeShop, on_delete=models.CASCADE, related_name='queues')
    queue_number = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    
    # Menggunakan auto_now_add=True adalah praktik yang lebih baik untuk timestamp pembuatan
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Antrian #{self.queue_number} di {self.coffee_shop.name}"

    class Meta:
        # --- ATURAN BARU YANG LEBIH KUAT ---
        # Memastikan nomor antrian unik untuk setiap coffee shop pada tanggal tertentu.
        # Kita tidak bisa menggunakan 'created_at__date' langsung di sini,
        # jadi kita akan menegakkan ini di logika view.
        # unique_together kita hapus untuk sementara agar tidak konflik.
        pass
# --- TAMBAHKAN MODEL BARU DI SINI ---
class PushSubscription(models.Model):
    # Endpoint unik yang diberikan oleh browser
    endpoint = models.URLField(max_length=500, unique=True)
    # Kunci untuk enkripsi
    p256dh = models.CharField(max_length=200)
    auth = models.CharField(max_length=200)
    # Terhubung ke coffee shop mana langganan ini
    coffee_shop = models.ForeignKey(CoffeeShop, on_delete=models.CASCADE, related_name='push_subscriptions')

    def __str__(self):
        return f"Subscription for {self.coffee_shop.name}"
