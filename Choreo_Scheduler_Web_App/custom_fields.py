from django.utils.translation import ugettext as _
from django.db import models

DAY_OF_THE_WEEK = {
    '1': _(u'Monday'),
    '2': _(u'Tuesday'),
    '3': _(u'Wednesday'),
    '4': _(u'Thursday'),
    '5': _(u'Friday'),
    '6': _(u'Saturday'),
    '7': _(u'Sunday'),
}

TIMES = ['9:00', '9:30', '10:00', '10:30', '11:00', '11:30',
         '12:00', '12:30', '13:00', '13:30', '14:00', '14:30',
         '15:00', '15:30', '16:00', '16:30', '17:00', '17:30',
         '18:00', '18:30', '19:00', '19:30', '20:00', '20:30',
         '21:00', '21:30', '22:00', '22:30', '23:00', '23:30']

class DayOfTheWeekField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices']=tuple(sorted(DAY_OF_THE_WEEK.items()))
        kwargs['max_length']=1 
        super(DayOfTheWeekField,self).__init__(*args, **kwargs)