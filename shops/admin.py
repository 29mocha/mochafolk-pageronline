# shops/admin.py
from django.contrib import admin
from .models import CoffeeShop, Queue, Profile, PushSubscription

admin.site.register(Profile)
admin.site.register(Queue)
admin.site.register(CoffeeShop)

@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('coffee_shop', 'endpoint_short')

    def endpoint_short(self, obj):
        # KUNCI PERBAIKAN: Langsung akses obj.endpoint
        if obj.endpoint:
            return "..." + obj.endpoint[-50:]
        return "N/A"
    endpoint_short.short_description = 'Endpoint'
