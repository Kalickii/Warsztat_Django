from django.shortcuts import render, redirect
from django.views import View
from django.utils.timezone import localdate

from datetime import date

from main.models import Room, Booking


class HomePageView(View):
    def get(self, request):
        return render(request, 'home.html')


class NewRoomView(View):
    def get(self, request):
        return render(request, 'new_room.html')

    def post(self, request):
        name = request.POST.get('name')
        capacity = int(request.POST.get('capacity'))
        projector = int(request.POST.get('projector'))
        if name and capacity > 0:
            if not Room.objects.filter(name=name).exists():
                Room.objects.create(name=name, capacity=capacity, have_projector=projector)
                return redirect('http://127.0.0.1:8000/')
            else:
                message = 'Error: Room already exists'
                return render(request, 'new_room.html', {'message': message})
        else:
            message = 'Error: Empty field or negative room capacity'
            return render(request, 'new_room.html', {'message': message})


class AllRoomsView(View):
    def get(self, request):
        if not Room.objects.all().exists():
            message = 'No rooms available'
            return render(request, 'home.html', {'message': message})
        else:
            rooms = Room.objects.all()
            room_status = {}
            rooms_with_status = []

            for room in rooms:
                room_status[room.id] = 'No'
                if Booking.objects.filter(room=room, date=localdate()).exists():
                    room_status[room.id] = 'Yes'

                rooms_with_status.append({
                    'id': room.id,
                    'name': room.name,
                    'capacity': room.capacity,
                    'have_projector': room.have_projector,
                    'status': room_status[room.id]
                })

            ctx = {'rooms': rooms_with_status}
            return render(request, 'all_room_list.html', ctx)


class RoomDeleteView(View):
    def get(self, request, room_id):
        room = Room.objects.get(pk=room_id)
        room.delete()
        return redirect('http://127.0.0.1:8000/room/list/')


class RoomModifyView(View):
    def get(self, request, room_id):
        room = Room.objects.get(pk=room_id)
        hidden_id = room_id
        ctx = {'room': room, 'hidden_id': hidden_id}
        return render(request, 'modify_room.html', ctx)

    def post(self, request, room_id):
        room = Room.objects.get(pk=room_id)
        name = request.POST.get('name')
        capacity = int(request.POST.get('capacity'))
        projector = int(request.POST.get('projector'))
        if name and capacity > 0:
            if not Room.objects.filter(name=name).exists() or name == room.name:
                room.name = name
                room.capacity = capacity
                room.have_projector = projector
                room.save()
                return redirect('http://127.0.0.1:8000/room/list')
            else:
                message = 'Error: Room already exists'
                return render(request, 'modify_room.html', {'message': message})
        else:
            message = 'Error: Empty field or negative room capacity'
            return render(request, 'modify_room.html', {'message': message})


class RoomBookView(View):
    def get(self, request, book_room_id):
        room = Room.objects.get(pk=book_room_id)
        bookings = Booking.objects.filter(room=room).order_by('date')
        ordered_bookings = [(booking.date, booking.comment) for booking in bookings]
        return render(request, 'book_room.html', {"room": room, 'bookings': ordered_bookings})

    def post(self, request, book_room_id):
        room = Room.objects.get(pk=book_room_id)
        book_date = request.POST.get('date')
        comment = request.POST.get('comment')
        bookings = Booking.objects.filter(room=room).order_by('date')
        ordered_bookings = [(booking.date, booking.comment) for booking in bookings]

        if Booking.objects.filter(room=room, date=book_date):
            message = "That room is already booked!"
            ctx = {"room": room, "message": message, "bookings": ordered_bookings}
            return render(request, 'book_room.html', ctx)
        if book_date < str(date.today()):
            message = "That date is from the past!"
            ctx = {"room": room, "message": message, "bookings": ordered_bookings}
            return render(request, 'book_room.html', ctx)

        Booking.objects.create(room=room, date=book_date, comment=comment)
        return redirect("http://127.0.0.1:8000/room/list")


class RoomDetailsView(View):
    def get(self, request, room_id):
        room = Room.objects.get(pk=room_id)
        bookings = Booking.objects.filter(room=room).order_by('date')
        ordered_bookings = [(booking.date, booking.comment) for booking in bookings]

        ctx = {
            'room': room, 'projector': 'Yes' if room.have_projector else 'No', 'bookings': ordered_bookings
               }

        return render(request, 'detailed_room.html', ctx)


class SearchView(View):
    def post(self, request):
        search_capacity = int(request.POST.get('search_capacity'))
        search_projector = int(request.POST.get('search_projector'))
        if search_capacity > 0:
            matching_rooms = Room.objects.filter(capacity__gte=search_capacity, have_projector=search_projector)

            room_status = {}
            available_rooms = []

            for room in matching_rooms:
                room_status[room.id] = 'No'
                if Booking.objects.filter(room=room, date=localdate()).exists():
                    room_status[room.id] = 'Yes'

                if room_status[room.id] == 'No':
                    available_rooms.append(room)

            return render(request, 'search.html', {'rooms': available_rooms})
        else:
            message = "Invalid search parameters"
            return render(request, 'home.html', {'message': message})
