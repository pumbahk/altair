from wtforms import Form, fields, validators
import logging
logger = logging.getLogger(__name__)
from webob.multidict import MultiDict

from altair.app.ticketing.core.models import TicketFormat
from altair.app.ticketing.core.models import Ticket
from altair.app.ticketing.core.models import ProductItem 

def parse(validator, postdata):
    if not hasattr(postdata, "getlist"):
        postdata = MultiDict(postdata)
    form = validator(postdata)
    if form.validate():
        return form.data 
    logger.warn(form.errors)
    return None

class SVGTransformValidator(Form):
    sx = fields.FloatField(default=1.0)
    sy = fields.FloatField(default=1.0)
    ticket_format = fields.IntegerField()

    def validate_ticket_format(form, field):
        if field.data is None:
            return
        ticket_format = TicketFormat.query.filter_by(id=field.data).first()
        if ticket_format is None:
            logger.warn("validation failure")
            raise validators.ValidationError("Ticket Format is not found")
        field.data = form.data["ticket_format"] = ticket_format

class FetchSVGFromModelsValidator(Form):
    """model_id -> model[has svg]"""
    model_name = fields.TextField()
    model = fields.TextField(default=object())
    model_candidates = ["Ticket"]

    def validate_model_name(form, field):
        if field.data and field.data not in form.model_candidates:
            raise validators.ValidatioinError("invalid model name %s" % field.data)

    def validate(self):
        if not super(FetchSVGFromModelsValidator, self).validate():
            return False
        model_name = self.data.get("model_name")
        if model_name == "Ticket":
            self.data["model"] = self.model.data = Ticket.query.filter_by(id=self.data["model"]).first()
            return True
        else:
            logger.warn("never call: model_name: %s (id=%s)" % (model_name,  self.data.get("model")))
            return False

class FillValuesFromModelsValidator(Form):
    """model_id -> model[fillvalues source]"""
    model_name = fields.TextField()
    model = fields.TextField(default=object())
    model_candidates = ["ProductItem"]

    def validate_model_name(form, field):
        if field.data and field.data not in form.model_candidates:
            raise validators.ValidatioinError("invalid model name %s" % field.data)

    def validate(self):
        if not super(FillValuesFromModelsValidator, self).validate():
            return False
        model_name = self.data.get("model_name")
        if model_name is None:
            return True
        elif model_name == "ProductItem":
            self.data["model"] = self.model.data = ProductItem.query.filter_by(id=self.data["model"]).first()
            return True
        else:
            logger.warn("never call: model_name: %s (id=%s)" % (model_name,  self.data.get("model")))

