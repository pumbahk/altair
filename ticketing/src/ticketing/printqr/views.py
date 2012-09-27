import json
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from ticketing.qr import get_qrdata_builder
import logging
from . import utils 
logger = logging.getLogger(__name__)

@view_config(route_name="index", renderer="ticketing.printqr:templates/index.html")
def index_view(request):
    api_resource = {
        "api.ticket.data": request.route_url("api.ticket.data")
    }
    return dict(json=json, api_resource=api_resource)

@view_config(route_name="api.ticket.data", renderer="json", 
             request_param="qrsigned")
def ticket_data(context, request):
    signed = request.params["qrsigned"]
    builder = get_qrdata_builder(request)
    try:
        data = utils.ticketdata_from_qrdata(builder.data_from_signed(signed))
        return data
    except Exception as e:
        logger.warn("%s: %s" % (e.__class__.__name__,  str(e)))
        raise HTTPBadRequest
