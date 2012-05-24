import json
from pyramid.response import Response
from .interfaces import IAPIKeyValidator, IEventRepository

def validate_apikey(request, apikey):
    reg = request.registry
    validator = reg.getUtility(IAPIKeyValidator)
    return validator(apikey)
    
def parse_and_save_event(request, data):
    reg = request.registry
    repository = reg.getUtility(IEventRepository)
    return repository.parse_and_save_event(data)

def json_error_response(errors):
    return Response(
        json.dumps(errors),
        content_type='application/json',
        status=400,
        )

