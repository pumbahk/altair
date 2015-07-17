from altair.jis.sjis import len_in_sjis
from wtforms.validators import ValidationError

class LengthInSJIS(object):
    def __init__(self, min=-1, max=-1, message=None):
        assert min != -1 or max!=-1, 'At least one of `min` or `max` must be specified.'
        assert max == -1 or min <= max, '`min` cannot be more than `max`.'
        self.min = min
        self.max = max
        self.message = message

    def __call__(self, form, field):
        l = field.data and len_in_sjis(field.data) or 0
        if l < self.min or self.max != -1 and l > self.max:
            if self.message is None:
                if self.max == -1:
                    self.message = field.ngettext('Field must be at least %(min)d character long.',
                                                  'Field must be at least %(min)d characters long.', self.min)
                elif self.min == -1:
                    self.message = field.ngettext('Field cannot be longer than %(max)d character.',
                                                  'Field cannot be longer than %(max)d characters.', self.max)
                else:
                    self.message = field.gettext('Field must be between %(min)d and %(max)d characters long.')

            raise ValidationError(self.message % dict(min=self.min, max=self.max))
