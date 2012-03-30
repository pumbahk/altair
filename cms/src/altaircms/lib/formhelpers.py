import wtforms.fields as fields

# class DateTimePickerField(fields.DateTimeField):
#     _kwargs = {"class_": "datepicker"}
#     def __call__(self, **kwargs):
#         defaults = self._kwargs.copy()
#         defaults.update(kwargs)
#         return super(DateTimePickerField, self).__call__(**defaults)

def datetime_pick_patch(): #slack-off
    _kwargs_defaults = {"class_": "datepicker"}

    from functools import wraps
    def with_args(method):
        @wraps(method)
        def wrapped(self, **kwargs):
            if not "class_" in kwargs:
                kwargs.update(_kwargs_defaults)
            return method(self, **kwargs)
        return wrapped
    target = fields.DateTimeField
    target.__call__ = with_args(target.__call__)
