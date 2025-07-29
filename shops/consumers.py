# shops/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

class QueueConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.shop_id = self.scope['url_route']['kwargs']['shop_pk']
        self.shop_group_name = f"queue_shop_{self.shop_id}"

        # PERBAIKAN: Tambahkan validasi shop_id
        try:
            shop_id_int = int(self.shop_id)
            if shop_id_int <= 0:
                await self.close()
                return
        except (ValueError, TypeError):
            await self.close()
            return

        # PERBAIKAN: Tambahkan error handling
        try:
            await self.channel_layer.group_add(
                self.shop_group_name,
                self.channel_name
            )
            await self.accept()
            
            # TAMBAHAN: Kirim konfirmasi koneksi
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': f'Connected to shop {self.shop_id}'
            }))
            
        except Exception as e:
            print(f"Error in WebSocket connect: {e}")
            await self.close()

    async def disconnect(self, close_code):
        # PERBAIKAN: Tambahkan error handling
        try:
            await self.channel_layer.group_discard(
                self.shop_group_name, 
                self.channel_name
            )
        except Exception as e:
            print(f"Error in WebSocket disconnect: {e}")

    async def receive(self, text_data):
        # PERBAIKAN: Tambahkan basic message handling
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'unknown')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'message': 'Server is alive'
                }))
        except json.JSONDecodeError:
            pass

    # Method untuk menangani update queue
    async def queue_update(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'queue_update',
            'message': message
        }))

    # Method untuk menangani queue baru
    async def queue_new(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'queue_new',
            'message': message
        }))

    # Method untuk pager ring
    async def pager_ring(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'pager_ring',
            'message': message
        }))