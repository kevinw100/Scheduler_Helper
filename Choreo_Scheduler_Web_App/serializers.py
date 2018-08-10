from rest_framework import serializers
from .models import Availability, Pairing, LeaderProfile
from django.contrib.auth.models import User

class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = '__all__'


class PairingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pairing
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class LeaderProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaderProfile
        fields = '__all__'


class OverlapSerializer(serializers.Serializer):
    day_of_week = serializers.CharField(max_length=1)
    time_of_day = serializers.TimeField()
