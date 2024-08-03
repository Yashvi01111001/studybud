from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
# Create your views here.

# rooms = [
#     {'id': 1, 'name': "let's learn python!"},
#     {'id': 2, 'name': "design with me!"},
#     {'id': 3, 'name': "frontend developers!"},
# ]

def loginPage(request):
    page = 'login'

#making sure if a user is already logged in we do not display login view again
#instead direct to home page
    if request.user.is_authenticated:
        return redirect('home')

# 1. getting the user credentials
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

# 2. checking if the user exists
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exist")

# 3. if the user exists we make sure that the credentials are correct
# also, we create the user object containing the username and password
        user = authenticate(request, email=email, password=password)

# 4. log the user in, this creates a session in the DB and the browser
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username or password does not exist")

    context={
        'page': page
    }
    return render(request, 'base/login_register.html', context)



def logoutUser(request):
    logout(request) #deletes the token (Right click on website -> Inspect -> Application -> Cookies)
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()

    #passing in the user data via POST:
    if request.method == 'POST':
        #throwing the data into the user creation form:
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            #making sure the username is cleaned (all in lowercase):
            user.username = user.username.lower()
            #registering the user:
            user.save()
            #logging in the user
            login(request, user)
            #redirecting the user back to the home page
            return redirect('home')
        else:
            #using a flash message
            messages.error(request, 'An error occured during registration')

    return render(request, 'base/login_register.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | #'i...' makes it case-insensitive
        Q(name__icontains=q) |
        Q(description__icontains=q)
    ) 
    
    # Yashuuuu you can figure out a way of displaying the top topics only below!!!
    # [0:5] means it shows the first 5 topics from index 0
    topics = Topic.objects.all()[0:5]

    room_count = rooms.count()

    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context =  {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages': room_messages
        }
    # render function takes 3 parameters
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    #message is the child model of room i.e. (Model) but we don't keep the initial in upper case
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    
    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants
        }
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        'user': user,
        'rooms': rooms,
        'room_messages': room_messages,
        'topics': topics
    }
    return render(request, 'base/profile.html', context)


#decorator: ensures that the below function is only accessible if user is logged in
#if a users sessionid is not in the browser, they will be redirected to the log in page
@login_required(login_url='login') 
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        # topic, created means get the topic that existed or get the created one (new one)
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        # creating a topic and then redirecting the user to home
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     #commit=False gies us an instance of the room:
        #     room = form.save(commit=False)
        #     #getting the host of the room as the user that is logged in
        #     #doing this step because we have excluded host field from the create room form via forms.py
        #     room.host = request.user
        #     room.save()
        return redirect('home')

    context = {
        'form': form,
        'topics': topics
        }
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed here!")

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        # topic, created means get the topic that existed or get the created one (new one)
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {
        'form': form,
        'topics': topics,
        'room': room
        }
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room })


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':message })


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})



def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})