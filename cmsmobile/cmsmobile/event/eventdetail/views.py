from pyramid.view import view_config
from altaircms.event.models import Event

class ValidationFailure(Exception):
    pass

@view_config(route_name='eventdetail', renderer='cmsmobile:templates/eventdetail/eventdetail.mako')
def move_eventdetail(request):
    event_id = request.params.get("event_id", None)
    event = request.allowable(Event).filter(Event.id == event_id).first()
    if not event:
        raise ValidationFailure
    return {
        'event':event
    }

@view_config(route_name='eventdetail', context=ValidationFailure, renderer='cmsmobile:templates/common/error.mako')
def failed_validation(request):
    return {}
