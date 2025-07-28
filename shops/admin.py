# shops/admin.py
from django.contrib import admin
from .models import CoffeeShop, Queue, Profile# Tambahkan Queue

# Daftarkan model Anda di sini
admin.site.register(CoffeeShop)
admin.site.register(Queue) # Daftarkan Queue
admin.site.register(Profile) # Daftarkan Profile