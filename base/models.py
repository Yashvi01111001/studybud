from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)

    avatar = models.ImageField(null=True, default="avatar.svg")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    # by default Null = False so we change above
    # blank allows an empty form to be submitted
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    # auto_now takes a time stamp everytime we save
    # while auto_now_add takes a timestamp only once when we create the instance

    # ordering the newest updated item to be at the top by using (-)
    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name
    

class Message(models.Model):
    # creating a one-to-many relationships for user, room
    #CASCADE means when the parent is deleted all the children are also deleted
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    # ordering the newest updated item to be at the top by using (-)
    class Meta:
        ordering = ['-updated', '-created']
    #string representation to output first 50 chars instead of whole message ('body')
    def __str__(self):
        return self.body[0:50]
    