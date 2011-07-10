import django.core.exceptions
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict
from django.utils.encoding import smart_unicode, smart_str
from django.forms.fields import Field
import datetime, re

class TimeDelta(datetime.timedelta):
    values_in_microseconds = SortedDict((
        # Uncomment the following two lines for year and month support
        # ('y', 31556925993600), # 52.177457 * (7*24*60*60*1000*1000)
        # ('m', 2629743832800), # 4.34812141 * (7*24*60*60*1000*1000)
        ('w', 604800000000), # 7*24*60*60*1000*1000
        ('d', 86400000000), # 24*60*60*1000*1000
        ('h', 3600000000), # 60*60*1000*1000
        ('m', 60000000), # 60*1000*1000
        ('s',  1000000), # 1000*1000
        ('ms', 1000),
        ('us', 1),
    ))
    
    def from_string(cls, value):
        if value == '0' or value == '0.000000':
            return datetime.timedelta.__new__(TimeDelta)
        
        pairs = []
        # The regex transforms strings such as "1h20m" into "1h 20m"
        # which .split is able to handle
        for b in re.sub(r"(\D)(\d)", r"\1 \2", value.lower()).split():
            for index, char in enumerate(b):
                if not char.isdigit():
                    pairs.append((b[:index], b[index:])) #digits, letters
                    break
        if not pairs:
            raise ValueError("Incorrect TimeDelta value")
    
        microseconds = 0
        for digits, chars in pairs:
            if not digits or not chars:
                raise ValidationError("Incorrect TimeDelta pair")
            microseconds += int(digits) * TimeDelta.values_in_microseconds[chars]
        
        return datetime.timedelta.__new__(TimeDelta, microseconds=microseconds)
    
    from_string = classmethod(from_string)

    def __new__(self, days=0, seconds=0, microseconds=0, value=None):
        """
        Creates TimeDelta
        
        Use value to cast from other type, or
        days, seconds, and microseconds for timedelta-like construction
        """
        if value != None and (days or seconds or microseconds):
            raise ValueError("Using value argument with other arguments is prohibited.")
        if value:
            if isinstance(value, basestring):
                return TimeDelta.from_string(value)
            
#           if isinstance(value, datetime.timedelta):
#               microseconds = float(value)
            
            microseconds = float(value)
        
        return datetime.timedelta.__new__(TimeDelta, days, seconds, microseconds)

    def __unicode__(self):
        if not self:
            return u"0"
        vals = []
        mis = self.days * 24 * 3600 * 1000000 + self.seconds * 1000000 + self.microseconds
        for k in self.values_in_microseconds:
            if mis >= self.values_in_microseconds[k]:
                diff, mis = divmod(mis, self.values_in_microseconds[k])
                vals.append("%d%s" % (diff, k))
        return u" ".join(vals)
    
class DurationField(Field):
    default_error_messages = {
        'invalid': _(u'Enter a valid duration.'),
        'min_value': _(u'Ensure this self is greater than or equal to %(min)s.'),
        'max_value': _(u'Ensure this self is less than or equal to %(max)s.'),
    }

    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        super(DurationField, self).__init__(*args, **kwargs)
        self.min_value, self.max_value = min_value, max_value

    def to_timedelta(self, value):
        """
        Takes an Unicode self and converts it to a datetime.timedelta object.
        1y 7m 6w 3d 18h 30min 23s 10ms 150mis => 
         1 year 7 months 6 weeks 3 days 18 hours 30 minutes 23 seconds 10 milliseconds 150 microseconds
         => datetime.timedelta(624, 6155, 805126)
        """
        try:
            return TimeDelta(value=value)
        except ValueError:
            raise ValidationError(self.error_messages['invalid'])

    def from_timedelta(self, value):
        if not value:
            return u"0"
        return unicode(value)

    def clean(self, value):
        "Validates max_value and min_value. Returns a datetime.timedelta object."
        value = self.to_timedelta(value)

        if self.max_value is not None and value > self.max_value:
            raise ValidationError(self.error_messages['max_value'] % {'max': self.max_value})

        if self.min_value is not None and value < self.min_value:
            raise ValidationError(self.error_messages['min_value'] % {'min': self.min_value})

        return value
