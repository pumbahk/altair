from wtforms.form import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators
from altaircms.event.models import Event
from altaircms.lib.formhelpers import dynamic_query_select_field_factory

class PerformanceForm(Form):
    backend_performance_id = fields.IntegerField(validators=[validators.Required()])
    event = dynamic_query_select_field_factory(Event, allow_blank=False)
    title = fields.TextField()
    venue = fields.TextField()
    open_on = fields.DateTimeField()
    start_on = fields.DateTimeField()
    close_on = fields.DateTimeField()

class TicketForm(Form):
    orderno = fields.IntegerField()
    event = dynamic_query_select_field_factory(Event, allow_blank=False) ## performance?
    price = fields.IntegerField(validators=[validators.Required()])
    seattype = fields.TextField(validators=[validators.Required()])
