# utm/consumers.py
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.gis.geos import Point
from .models import FlightRoute
from channels.db import database_sync_to_async

class DroneConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.flight_id = self.scope['url_route']['kwargs']['flight_id']
        self.group_name = f'flight_{self.flight_id}'

        # Присоединяемся к группе, чтобы рассылать сообщения всем подписанным
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Убираем из группы при отключении
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')

        if command == 'start_simulation':
            # Запуск симуляции
            await self.simulate_flight()

    async def simulate_flight(self):
        try:
            route = await database_sync_to_async(FlightRoute.objects.get)(id=self.flight_id)
        except FlightRoute.DoesNotExist:
            await self.send(json.dumps({'error': 'Маршрут не найден'}))
            return

        # Получаем список точек маршрута
        points = route.path.coords  # Список кортежей (x, y)

        for coord in points:
            # Отправляем координаты в группу
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'send_coordinates',
                    'coordinates': {'lng': coord[0], 'lat': coord[1]}
                }
            )
            await asyncio.sleep(1)  # Пауза между обновлениями

    async def send_coordinates(self, event):
        # Отправляем данные клиенту
        await self.send(text_data=json.dumps({
            'coordinates': event['coordinates']
        }))