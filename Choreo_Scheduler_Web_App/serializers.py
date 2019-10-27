from rest_framework import serializers
from .models import Availability, Pairing, LeaderProfile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from .token_helpers import create_token, get_token_by_key, get_token_by_user
from django.db.utils import IntegrityError


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


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""
    username = serializers.CharField(max_length=255, min_length=4)
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )
    # The client should not be able to send a token along with a registration
    # request. Making `token` read-only handles that for us.

    def validate(self, data):
        print('received data: %s' % data)
        username = data.get("username", None)
        email = data.get("email", None)

        # TODO: add SHA256 to your client-side password
        password = data.get("password", None)
        
        if password is None:
            raise serializers.ValidationError("A password is required to register")

        if email is None:
            raise serializers.ValidationError("An email is required to register")

        if username is None: 
            raise serializers.ValidationError("A username is required to register")

        try:
            # Create user actually does the password hashing (don't use vanilla create - otherwise authenticate() won't work).
            new_user = User.objects.create_user(username=username, email=email, password=password)
        except IntegrityError as exception:
            print("[ERROR]: Received an invalid request due to: " + str(exception))
            raise serializers.ValidationError("Somebody has already signed up for your username. Please try another")

        return {
            'username': username,
            'email': email,
            'password': password,
            'id': new_user.id
        }

    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LogoutSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    token_key = serializers.CharField(min_length=40, max_length=40, write_only=True)

    def validate(self, data):
        # The `validate` method is where we make sure that the current
        # instance of `LoginSerializer` has "valid". In the case of logging a
        # user in, this means validating that they've provided an email
        # and password and that this combination matches one of the users in
        # our database.
        username = data.get('username', None)
        token_key = data.get('token_key', None)

        print("received username: %s" % username)

        if username is None:
            raise serializers.ValidationError(
                'A user name is required to logout'
            )

        # Will throw an exception if the user lacks a token
        try:
            user_token = get_token_by_key(token_key)        
        except Token.DoesNotExist as exception:
            print("[ERROR]: Received an invalid request due to: %s" % str(exception))
            raise serializers.ValidationError(
                'Token key provided does not exist. Please make sure you are not already logged out'
            )

        # Check that passed token actually matches username provided
        if not(user_token.user.username == username):
            raise serializers.ValidationError(
                'Token provided does not correspond to the given user'
            )

        print("attempting to delete user_token: %s with key: %s" % (repr(user_token), user_token.key))
        user_token.delete()

        # The `validate` method should return a dictionary of validated data.
        # This is the data that is passed to the `create` and `update` methods
        return {
            'username': username,
            'token': user_token.key
        }

    class Meta:
        model = Token
        fields = ['key', 'user.username']


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        # The `validate` method is where we make sure that the current
        # instance of `LoginSerializer` has "valid". In the case of logging a
        # user in, this means validating that they've provided an email
        # and password and that this combination matches one of the users in
        # our database.
        print('received data in validate: %s' % data)
        username = data.get('username', None)
        password = data.get('password', None)

        # As mentioned above, an email is required. Raise an exception if an
        # email is not provided.
        if username is None:
            raise serializers.ValidationError(
                'A user name is required to log in.'
            )

        # As mentioned above, a password is required. Raise an exception if a
        # password is not provided.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        # The `authenticate` method is provided by Django and handles checking
        # for a user that matches this username/password combination.
        user = authenticate(username=username, password=password)
        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        if user is None:
            print("[ERROR]: attempted login from username: %s using password %s failed auth" % (username, password))
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        # Not sure if I'll ever impl deactivating users
        if not user.is_active:
            print("[ERROR]: user %s is not active and attempted to login")
            raise serializers.ValidationError(
                'The selected user has been marked as inactive'
            )

        user_token, _ = Token.objects.get_or_create(user=user)
        print("[INFO] successfully created token for user %s" % user)

        # The `validate` method should return a dictionary of validated data.
        # This is the data that is passed to the `create` and `update` methods
        return {
            'email': user.email,
            'username': user.username,
            'token': user_token.key
        }


class OverlapSerializer(serializers.Serializer):
    day_of_week = serializers.CharField(max_length=1)
    time_of_day = serializers.TimeField()
