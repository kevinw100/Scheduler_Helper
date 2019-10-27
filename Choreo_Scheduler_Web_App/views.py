from rest_framework import authentication, permissions, viewsets, status

from .models import Availability, LeaderProfile, Pairing
from .serializers import AvailabilitySerializer, \
                         PairingsSerializer, \
                         UserSerializer, \
                         LeaderProfileSerializer, \
                         OverlapSerializer, \
                         LoginSerializer, \
                         RegistrationSerializer, \
                         LogoutSerializer
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from .custom_fields import DAY_OF_THE_WEEK, TIMES
import time
import calendar


class DefaultsMixin(object):
    """Default settings for view authentication, permissions, filtering and pagination."""
    '''
        This app has token authentication installed (HTTPS remains a todo). Any view that includes
        this Mixin automatically gains this authentication. To submit a request,
        try: curl -X 'http:/<your_url_here>/' -H 'Authorization: Token <your_token>'
        You can get your token from the "Tokens DB" (see populate_db_scripts for the import)
    '''

    authentication_classes = (
        authentication.TokenAuthentication,
    )

    permission_classes = (
        permissions.IsAuthenticated,
    )
    paginate_by = 25
    paginate_by_param = 'page_size'
    max_paginate_by = 100

'''
    For registering New Users. User must be passed in as a form JSON with the following format:
    {
        "email":<email>,
        "username":<username>,
        "password":<password>
    }
'''


class ScheduleEncodings(APIView):
    @staticmethod
    def _parse_to_epoch_second(time_str):
        time_obj = time.strptime(time_str, '%H:%M')
        return calendar.timegm(time_obj)

    def get(self, request):
        # since it's a simple lookup, don't really need a serializer to parse through requests.
        num_times = len(TIMES)
        interval = (ScheduleEncodings._parse_to_epoch_second(TIMES[1]) - ScheduleEncodings._parse_to_epoch_second(TIMES[0])) / 60
        start_time = TIMES[0]
        response_dict =  {
            'days_encoding': DAY_OF_THE_WEEK,
            'num_times': num_times,
            'start_time': start_time,
            'interval': interval
        }
        return Response(response_dict, status=status.HTTP_200_OK)


class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data
        print("received user: %s" % user)
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        print("serialized data: %s" % serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LogoutAPIView(APIView):
    # TODO: change this to allow only authenticated users post their data to this endpoint (extend defaultsmixin)

    permission_classes = (permissions.AllowAny,)
    serializer_class = LogoutSerializer

    def post(self, request):
        print("logout data is: %s" % request.data)

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LoginAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    @csrf_exempt
    def post(self, request):
        user = request.data
        print("user is: %s" % user)
        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class AvailabilitiesSingleUser(DefaultsMixin, viewsets.ViewSet):
    """API Endpoint for viewing availabilities"""
    def list(self, request, format=None):
        curr_user = request.user
        print("[INFO] getting availabilities for user: %s" % curr_user)
        queryset = Availability.objects.filter(owner=curr_user)
        if(queryset.)
        serializer = AvailabilitySerializer(queryset, many=len(queryset) > 1)
        return Response(serializer.data)

    # TODO: refactor to allow this to handle multiple requests
    def create(self, request, format=None):
        user_id = request.user
        time_data = request.data
        time_data['owner'] = user_id
        Availability.objects.create(**time_data)
        return Response(status=status.HTTP_201_CREATED)


class AvailabilitiesAllUsers(DefaultsMixin, viewsets.ReadOnlyModelViewSet):
    # TODO: make this only readable by "Super Users (by performing a group check)"
    # After, make it that only "organizers" can actually put get the availabilities
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer


class LeaderPromotionsViewSet(viewsets.ModelViewSet):
    queryset = LeaderProfile.objects.all()
    serializer_class = LeaderProfileSerializer


class PairingsViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """API Endpoint for viewing meeting leaders (Choreographers, etc)"""
    queryset = Pairing.objects.all()
    serializer_class = PairingsSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PairingsOverlapViewSet(DefaultsMixin, viewsets.ViewSet):
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


class UsersAvailable(DefaultsMixin, APIView):
    def get(self, request, time_of_day, day_of_week):
        # print("time of day: %s, day of week: %s" % (time_of_day, DAY_OF_THE_WEEK[day_of_week]))
        user_data = User.objects.filter(availability__time_of_day=time_of_day, availability__day_of_week=day_of_week)
        serializer = UserSerializer(user_data, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
