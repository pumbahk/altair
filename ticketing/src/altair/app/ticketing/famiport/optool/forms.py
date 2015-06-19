from altair.formhelpers.form import OurForm
from altair.formhelpers.fields import OurTextField
from altair.formhelpers.widgets import OurPasswordInput
from wtforms.validators import Required, Length

class LoginForm(OurForm):
    user_name = OurTextField(
        validators=[
            Required(),
            Length(max=32)
            ]
        )
    password = OurTextField(
        widget=OurPasswordInput(),
        validators=[
            Required()
            ]
        )

