import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

class SeatAvailabilityConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.schedule_id = self.scope['url_route']['kwargs']['schedule_id']
        self.room_group_name = f'seat_availability_{self.schedule_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        status = await self.get_seat_status()
        await self.send(text_data=json.dumps({'type':'initial_state','data':status}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('action') == 'lock_seat':
            seat_id = data['seat_id']
            if await self.lock_seat(seat_id):
                await self.channel_layer.group_send(self.room_group_name,
                    {'type':'seat_update','seat_id':str(seat_id),'status':'locked','user':self.scope['user'].email})

    async def seat_update(self, event):
        await self.send(text_data=json.dumps({
            'type':'seat_update','seat_id':event['seat_id'],'status':event['status'],'user':event.get('user','')
        }))

    @database_sync_to_async
    def get_seat_status(self):
        from apps.schedules.models import Schedule
        from apps.vehicles.models import Seat
        from apps.bookings.models import BookingSeat, SeatLock
        schedule = Schedule.objects.get(id=self.schedule_id)
        seats = Seat.objects.filter(vehicle=schedule.vehicle)
        booked = set(BookingSeat.objects.filter(booking__schedule=schedule,
            booking__status__in=['CONFIRMED','BOARDED']).values_list('seat_id', flat=True))
        locked = set(SeatLock.objects.filter(schedule=schedule, is_active=True,
            expires_at__gt=timezone.now()).values_list('seat_id', flat=True))
        seat_data = []
        for seat in seats:
            status = 'available'
            if seat.id in booked: status = 'booked'
            elif seat.id in locked: status = 'locked'
            seat_data.append({'id':str(seat.id),'number':seat.seat_number,'type':seat.seat_type,'status':status,'row':seat.row,'column':seat.column})
        return {'seats':seat_data,'total_seats':schedule.vehicle.capacity,'available_seats':schedule.available_seats,'booked_seats':schedule.booked_seats}

    @database_sync_to_async
    def lock_seat(self, seat_id):
        from apps.bookings.models import SeatLock
        from apps.schedules.models import Schedule
        schedule = Schedule.objects.get(id=self.schedule_id)
        lock, created = SeatLock.objects.get_or_create(schedule=schedule, seat_id=seat_id,
            defaults={'session_key':self.scope['user'].email, 'expires_at':timezone.now()+timezone.timedelta(seconds=300)})
        return created