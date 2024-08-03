# GOT THIS ERROR SO WE NEED THIS SERIALIZERS FILE:
# TypeError at /api/rooms/
# Object of type Room is not JSON serializable
# Request Method:	GET
# Request URL:	http://127.0.0.1:8000/api/rooms/

# serializers are classes that take a certain model/ 
# object that we want to serilaize and turns it into json data
# basically, it takes our python object and turns it into 
# a json object so that it can be returned on the web

from rest_framework.serializers import ModelSerializer
from base.models import Room

# We are taking all the fields in the Room model in models.py,
# then returning them and  turning them into json objects:
class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
    