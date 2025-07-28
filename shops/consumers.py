# shops/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class QueueConsumer(AsyncWebsocketConsumer):
    # GANTI SELURUH METHOD CONNECT DENGAN INI
    async def connect(self):
        self.shop_id = self.scope['url_route']['kwargs']['shop_pk']
        self.shop_group_name = f"queue_shop_{self.shop_id}"

        # Langsung terima koneksi tanpa cek keamanan
        await self.channel_layer.group_add(
            self.shop_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.shop_group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    # Method ini menangani pesan saat status diubah menjadi 'ready'
    async def queue_update(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'queue_update', # Tambahkan tipe di payload
            'message': message
        }))

    # --- TAMBAHKAN METHOD BARU DI SINI ---
    # Method ini menangani pesan saat ada antrian baru dibuat
    async def queue_new(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'queue_new', # Tambahkan tipe di payload
            'message': message
        }))

     # --- TAMBAHKAN METHOD BARU DI SINI ---
    async def pager_ring(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'pager_ring',
            'message': message
        }))