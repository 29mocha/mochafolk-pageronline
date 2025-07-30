# shops/admin.py
from django.contrib import admin
from .models import CoffeeShop, Queue, Profile, PushSubscription

# Daftarkan model Profile
admin.site.register(Profile)

# Daftarkan model Queue
admin.site.register(Queue)

# Daftarkan model CoffeeShop
admin.site.register(CoffeeShop)

# --- TAMBAHKAN INI UNTUK MENAMPILKAN PUSH SUBSCRIPTION ---
@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('coffee_shop', 'endpoint_short')

    def endpoint_short(self, obj):
        # Tampilkan hanya 30 karakter terakhir dari endpoint agar tidak terlalu panjang
        endpoint_str = obj.subscription_data.get('endpoint', '')
        return "..." + endpoint_str[-30:]
    endpoint_short.short_description = 'Endpoint'

