from django.db import models
from django.contrib.auth.models import User
from .custom_fields import DayOfTheWeekField


# Users only appear in when they are a group leader
class LeaderProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return "Leader: %s" % self.user

    '''    
        Creation Factories
    '''
    @staticmethod
    def promote_by_first_last_name(self, first_name, last_name):
        promotee = User.objects.get(first_name=first_name, last_name=last_name)
        return LeaderProfile(user=promotee)


# Populated for every 30 minute interval
class Availability(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    time_of_day = models.TimeField()
    day_of_week = DayOfTheWeekField()

    def __str__(self):
        return "available on %s at %s with uid %s" % (self.day_of_week, self.time_of_day, self.owner)


# Set of Pairings of group leaders (if no pairing, then points to same user)
class Pairing(models.Model):
    from_node = models.ForeignKey(LeaderProfile,
                                  on_delete=models.CASCADE,
                                  verbose_name="First Leader",
                                  related_name="first_leader")

    to_node = models.ForeignKey(LeaderProfile,
                                on_delete=models.CASCADE,
                                verbose_name="Second Leader",
                                related_name="second_leader")

    def __str__(self):
        return "u1: %s %s; username %s and u2: %s %s; username %s" % \
               (self.from_node.user.first_name,
                self.from_node.user.last_name,
                self.from_node.user,
                self.to_node.user.first_name,
                self.to_node.user.last_name,
                self.to_node.user)
