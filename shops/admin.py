# shops/admin.py
from django.contrib import admin
from .models import CoffeeShop, Queue, Profile, PushSubscription

# Daftarkan model Profile
admin.site.register(Profile)

# Daftarkan model Queue
admin.site.register(Queue)

# Daftarkan model CoffeeShop
admin.site.register(CoffeeShop)

# --- KUNCI PERBAIKAN: Buat tampilan admin lebih aman ---
@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('coffee_shop', 'endpoint_short', 'created_at_formatted')
    list_filter = ('coffee_shop',)
    search_fields = ('subscription_data__endpoint',)

    def endpoint_short(self, obj):
        # Cek apakah data valid sebelum diakses
        if isinstance(obj.subscription_data, dict):
            endpoint_str = obj.subscription_data.get('endpoint', '')
            if endpoint_str:
                return "..." + endpoint_str[-50:]
        return "N/A" # Tampilkan N/A jika data tidak valid
    endpoint_short.short_description = 'Endpoint'

    def created_at_formatted(self, obj):
        # Cek apakah objek punya created_at (seharusnya selalu ada)
        if hasattr(obj, 'created_at') and obj.created_at:
            return obj.created_at.strftime("%Y-%m-%d %H:%M")
        return "N/A"
    created_at_formatted.short_description = 'Waktu Dibuat'

