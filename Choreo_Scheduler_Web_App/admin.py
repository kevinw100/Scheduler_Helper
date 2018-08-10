from django.contrib import admin
from .models import Availability, Pairing, LeaderProfile

admin.site.register(Availability)
admin.site.register(Pairing)
admin.site.register(LeaderProfile)