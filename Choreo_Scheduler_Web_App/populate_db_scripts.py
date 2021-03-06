from .models import Availability
from django.contrib.auth.models import User
from .custom_fields import TIMES
import itertools

def populate_all_availabilities_for_user(username):
    user = User.objects.get(username=username)
    days_of_week = list(range(1,8))

    for (t_o_d, d_o_w) in itertools.product(TIMES, days_of_week):
        Availability(owner=user, time_of_day=t_o_d, day_of_week=d_o_w).save()

    print("Availabilities Filled!")


def remove_all_availabilities_for_user(username):
    user = User.objects.get(username=username)
    Availability.objects.filter(owner=user).delete()

    print("Availabilities Deleted!")