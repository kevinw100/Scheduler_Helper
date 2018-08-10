from rest_framework import authentication, permissions, viewsets, status

from .models import Availability, LeaderProfile, Pairing
from .serializers import AvailabilitySerializer, PairingsSerializer, UserSerializer, LeaderProfileSerializer, OverlapSerializer
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from django.db.models import ObjectDoesNotExist, F
from rest_framework.views import  APIView

class DefaultsMixin(object):
    """Default settings for view authentication, permissions, filtering and pagination."""

    authentication_classes = (
        authentication.BasicAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )
    paginate_by = 25
    paginate_by_param = 'page_size'
    max_paginate_by = 100


class AvailabilitiesSingleUser(viewsets.ViewSet):
    """API Endpoint for viewing availabilities"""
    def list(self, request, format=None):
        curr_user = request.user
        queryset = Availability.objects.filter(owner=curr_user)
        print(queryset)
        serializer = AvailabilitySerializer(queryset, many=len(queryset) > 1)
        return Response(serializer.data)

    # TODO: refactor to allow this to handle multiple requests
    def create(self, request, format=None):
        user_id = request.user
        time_data = request.data
        time_data['owner'] = user_id
        Availability.objects.create(**time_data)
        return Response(status=status.HTTP_201_CREATED)


class AvailabilitiesAllUsers(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer


class LeaderPromotionsView(viewsets.ModelViewSet):
    queryset = LeaderProfile.objects.all()
    serializer_class = LeaderProfileSerializer


class PairingsViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """API Endpoint for viewing meeting leaders (Choreographers, etc)"""
    queryset = Pairing.objects.all()
    serializer_class = PairingsSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PairingsOverlapViewSet(viewsets.ViewSet):
    """API Endpoint for viewing Overlapping Pairing Availability"""
    @staticmethod
    # Used to check for equality of day of week and time of day
    def _create_dt_string(qs_entry):
        return "%s_%s" % (qs_entry.day_of_week, qs_entry.time_of_day)

    @staticmethod
    def _determine_overlaps(qs1, qs2):
        qs1_set = set(map(PairingsOverlapViewSet._create_dt_string, set(qs1)))
        overlaps = []

        for qs_obj in list(qs2):
            if PairingsOverlapViewSet._create_dt_string(qs_obj) in qs1_set:
                overlaps.append({'time_of_day': qs_obj.time_of_day,
                                 'day_of_week': qs_obj.day_of_week})
        return overlaps

    def retrieve(self, request, pk, format=None):
        pairing = Pairing.objects.get(pk=pk)
        from_avails = Availability.objects.filter(owner=pairing.from_node.user)
        to_avails = Availability.objects.filter(owner=pairing.to_node.user)
        overlaps = PairingsOverlapViewSet._determine_overlaps(to_avails, from_avails)
        serializer = OverlapSerializer(data=overlaps, many=True)
        if serializer.is_valid():
            return Response(data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UsersAvailable(APIView):
    def get(self, request, time_of_day, day_of_week):
        print("day of week: %s \n time_of_day: %s" % (day_of_week, time_of_day))
        user_data = User.objects.filter(availability__time_of_day=time_of_day, availability__day_of_week=day_of_week)
        print(user_data)
        serializer = UserSerializer(user_data, many=True)
        print(serializer.data)
        return Response(data=serializer.data, status=status.HTTP_200_OK)