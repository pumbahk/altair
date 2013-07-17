from wtforms.widgets.core import Input

class OurTextInput(Input):
    input_type = 'text'

    def __call__(self, field, **kwargs):
        if 'placeholder' not in kwargs:
            kwargs['placeholder'] = field.label.text
        return super(OurTextInput, self).__call__(field, **kwargs)
