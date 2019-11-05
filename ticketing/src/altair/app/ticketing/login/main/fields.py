from wtforms.fields import TextField

__all__ = (
  'DisabledTextField',
  )

class DisabledTextField(TextField):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('disabled', True)
        return super(DisabledTextField, self).__call__(*args, **kwargs)
