# -*- coding:utf-8 -*-

from decimal import Decimal
import sqlalchemy.orm as orm
import json
import base64
from StringIO import StringIO
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from jsonrpclib import jsonrpc
from pyramid.httpexceptions import HTTPBadRequest
from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID
import logging
logger = logging.getLogger(__name__)

from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.tickets.utils import transform_matrix_from_ticket_format
from altair.app.ticketing.tickets.utils import build_dict_from_product
from altair.app.ticketing.tickets.utils import build_dict_from_venue
from altair.app.ticketing.tickets.utils import build_dict_from_event
from altair.app.ticketing.tickets.utils import build_dict_from_organization

from .api import SVGPreviewCommunication
from .api import SEJPreviewCommunication
from .api import as_filelike_response

from .transform import SVGTransformer
from .transform import FillvaluesTransformer
from .transform import SEJTemplateTransformer

from .fillvalues import template_collect_vars
from .fillvalues import template_fillvalues
from .fetchsvg import fetch_svg_from_postdata
from ..cleaner.api import get_validated_svg_cleaner
from ..response import FileLikeResponse
# todo: refactoring
from ..utils import build_dict_from_product_item
from altair.svg.geometry import parse_transform

from . import TicketPreviewAPIException
from . import TicketPreviewTransformException
from . import TicketPreviewFillValuesException
from ..cleaner.api import TicketCleanerValidationError

## todo move it
def decimal_converter(target, converter=float):
    """ for product.price ... etc"""
    if isinstance(target, (list, tuple)):
        for e in target:
            decimal_converter(e, converter=converter)
    elif hasattr(target, "keys"):
        for k in target.keys():
            v = target.get(k)
            if isinstance(v, Decimal):
                target[k] = converter(v)
            else:
                decimal_converter(v, converter)
        return target


def route_path_with_params(request, url, _query=None, **kwargs):
    """
    request.route_path("http://foo.bar.net", _query(query=None)) => "http://foo.bar.net/"
    request.route_path("http://foo.bar.net", _query(query="exists-value")) => "http://foo.bar.net/?query=exists-value"
    """
    if _query:
        for k in _query.keys():
            v = _query[k]
            if v is None or v == "None": # todo: refactoring
                del _query[k]
    return request.route_path(url, _query=_query, **kwargs)

def _build_ticket_format_dicts(ticket_format_qs):
    sej_qs = ticket_format_qs.filter(
        c_models.TicketFormat.id==c_models.TicketFormat_DeliveryMethod.ticket_format_id,
        c_models.TicketFormat_DeliveryMethod.delivery_method_id==c_models.DeliveryMethod.id, 
        c_models.DeliveryMethod.delivery_plugin_id==SEJ_DELIVERY_PLUGIN_ID)

    D = {}
    for t in ticket_format_qs:
        D[t.id] = {"name": t.name, "type": ""}
    for t in sej_qs:
        D[t.id] = {"name": t.name, "type": ":sej"}
    return [dict(pk=k, **vs) for k, vs in D.iteritems()]

def _build_ticket_format_dict(ticket_format):
    has_sej = any(dm.delivery_plugin_id == SEJ_DELIVERY_PLUGIN_ID for dm in ticket_format.delivery_methods)
    ticket_format_type =  ":sej" if has_sej else ""
    return {"pk": ticket_format.id, "name": ticket_format.name, "type": ticket_format_type}

@view_config(route_name="tickets.preview", request_method="GET", renderer="altair.app.ticketing:templates/tickets/preview.html", 
             decorator=with_bootstrap, permission="event_editor")
def preview_ticket(context, request):
    apis = {
        "normalize": request.route_path("tickets.preview.api", action="normalize"), 
        "previewbase64": request.route_path("tickets.preview.api", action="preview.base64"), 
        "collectvars": request.route_path("tickets.preview.api", action="collectvars"), 
        "fillvalues": request.route_path("tickets.preview.api", action="fillvalues"), 
        "fillvalues_with_models": request.route_path("tickets.preview.api", action="fillvalues_with_models"), 
        "combobox": request.route_path("tickets.preview.combobox")
        }
    ticket_formats = c_models.TicketFormat.query.filter_by(organization_id=context.user.organization_id)
    ticket_formats = _build_ticket_format_dicts(ticket_formats)
    return {"apis": apis, "ticket_formats": ticket_formats}


@view_config(route_name="tickets.preview", request_method="POST", permission='sales_counter')
def preview_ticket_post(context, request):
    """
    curl -Fsvgfile=@<file> <url> > out.png
    """
    preview = SVGPreviewCommunication.get_instance(request)
    if "raw" in request.POST:
        svg_string = request.POST["svgfile"].file.read()
    else:
        svgio = request.POST["svgfile"].file 
        cleaner = get_validated_svg_cleaner(svgio, exc_class=HTTPBadRequest)
        svgio = cleaner.get_cleaned_svgio()
        svg_string = svgio.getvalue()
    try:
        imgdata_base64 = preview.communicate(request, svg_string)
        return as_filelike_response(request, base64.b64decode(imgdata_base64))
    except jsonrpc.ProtocolError, e:
        raise HTTPBadRequest(str(e))


@view_config(route_name="tickets.preview", request_method="POST", permission='sales_counter', request_param="type=sej") # +svgfile
def preview_ticket_post_sej(context, request):
    preview = SEJPreviewCommunication.get_instance(request)

    svgio = request.POST["svgfile"].file
    transform_str = request.POST.get("transform")
    transform = parse_transform(transform_str) if transform_str else None
    cleaner = get_validated_svg_cleaner(svgio, exc_class=HTTPBadRequest)
    svgio = cleaner.get_cleaned_svgio()
    svgio.seek(0)

    ptct = SEJTemplateTransformer(svgio=svgio, transform=transform).transform()
    imgdata = preview.communicate(request, ptct)
    return as_filelike_response(request, imgdata)


@view_config(route_name="tickets.preview.download", request_method="POST", permission='sales_counter', request_param="svg")
def preview_ticket_download(context, request):
    io = StringIO(request.POST["svg"].encode("utf-8"))
    return FileLikeResponse(io, request=request, filename="preview.svg")


@view_config(route_name="tickets.preview.enqueue", request_method="POST", permission='sales_counter', request_param="svg", renderer="json")
def ticket_preview_enqueue(context, request):
    svg = request.POST["svg"]
    ticket_format_id = request.POST["ticket_format_id"]
    ticket = c_models.Ticket.query.filter(c_models.Ticket.ticket_format_id==ticket_format_id, 
                                          c_models.Ticket.event==None).first()
    try:
        c_models.TicketPrintQueueEntry.enqueue(
            context.user,  
            ticket, 
            data=dict(drawing=svg),                                                   
            summary=u'券面テンプレート (preview)',
            ) #todo seat
        return {"status": True, "data": "ok"}
    except Exception, e:
        logger.exception(e)
        return {"status": False, "message": "%s: %s" % (e.__class__.__name__, str(e))}


@view_config(route_name="tickets.preview.combobox", request_method="GET", renderer="altair.app.ticketing:templates/tickets/combobox.html", 
             decorator=with_bootstrap, permission="event_editor")
@view_config(route_name="tickets.preview.combobox", request_method="GET", renderer="altair.app.ticketing:templates/tickets/_combobox.html", 
             permission="event_editor", xhr=True)
def combbox_for_preview(context, request):
    get = request.GET.get
    apis = {
        "organization_list": request.route_path("tickets.preview.combobox.api", model="organization"), 
        "event_list": route_path_with_params(request, "tickets.preview.combobox.api", model="event", _query=dict(event_id=get("event_id"))), 
        "performance_list": route_path_with_params(request, "tickets.preview.combobox.api", model="performance", _query=dict(performance_id=get("performance_id"))),  
        "product_list": route_path_with_params(request, "tickets.preview.combobox.api", model="product", _query=dict(product_id=get("product_id"))),  
        }
    return {"organization": context.organization, "apis": apis}

#api
"""
raw svg -> normalize svg -> base64 png
"""
@view_defaults(route_name="tickets.preview.api", request_method="POST", renderer="json", permission='sales_counter')
class PreviewApiView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(match_param="action=loadsvg")
    def preview_api_loadsvg(self): #deprecated
        """
        data = {"for_svg": {"model_name": "TicketBundle", model: 1}, 
                "for_fillvalues": {"model_name": "ProductItem", model: 1}}
        """
        try:
            data = json.loads(self.request.POST["data"])
            svg = fetch_svg_from_postdata(data.get("for_svg", {}))
            if svg is None:
                return {"status": False, "data": svg, "message": "svg is not found"}
            svg = FillvaluesTransformer(svg, data.get("for_fillvalues", {})).transform()
            return {"status": True, "data": svg}
        except TicketPreviewAPIException, e:
            return {"status": False, "message": "%s" % e.message}
        except Exception, e:
            logger.exception(e)
            return {"status": False, "message": "%s: %s" % (e.__class__.__name__, str(e))}

    @view_config(match_param="action=normalize", request_param="svg")
    def preview_api_normalize(self):
        try:
            svgio = StringIO(unicode(self.request.POST["svg"]).encode("utf-8")) #unicode only
            cleaner = get_validated_svg_cleaner(svgio, exc_class=Exception)
            svgio = cleaner.get_cleaned_svgio()
            return {"status": True, "data": svgio.getvalue()}
        except TicketCleanerValidationError, e:
            return {"status": False, "message": e.message}
        except Exception, e:
            logger.exception(e)
            return {"status": False, "message": "%s: %s" % (e.__class__.__name__, str(e))}


    @view_config(match_param="action=preview.base64")
    def preview_ticket_post64(self):
        preview = SVGPreviewCommunication.get_instance(self.request)
        svg = self.request.POST["svg"]
        try:
            transformer = SVGTransformer(svg, self.request.POST)
            svg = transformer.transform()
            imgdata_base64 = preview.communicate(self.request, svg)
            return {"status": True, "data":imgdata_base64, 
                    "width": transformer.width, "height": transformer.height} #original size
        except TicketPreviewTransformException, e:
            return {"status": False, "message": "%s" % e.message}            
        except TicketPreviewAPIException, e:
            return {"status": False, "message": "%s" % e.message}
        except Exception, e:
            logger.exception(e)
            return {"status": False, "message": "%s: %s" % (e.__class__.__name__, str(e))}


    @view_config(match_param="action=preview.base64", request_param="type=sej") #svg
    def preview_ticket_post64_sej(self):
        try:
            preview = SEJPreviewCommunication.get_instance(self.request)

            ticket_format_id = self.request.POST["ticket_format"]
            ticket_format = c_models.TicketFormat.query.filter_by(id=ticket_format_id).first()
            if ticket_format is None:
                logger.warn("ticket format %s is not found" % ticket_format_id)
                global_transform = None
            else:
                global_transform = transform_matrix_from_ticket_format(ticket_format)

            transformer = SEJTemplateTransformer(svgio=StringIO(self.request.POST["svg"]), global_transform=global_transform)
            ptct = transformer.transform()
            imgdata = preview.communicate(self.request, ptct)
            return {"status": True, "data":base64.b64encode(imgdata), 
                    "width": transformer.width, "height": transformer.height} #original size
        except TicketPreviewFillValuesException, e:
            return {"status": False, "message": "%s" % e.message}
        except TicketPreviewTransformException, e:
            return {"status": False, "message": "%s" % e.message}            
        except TicketPreviewAPIException, e:
            return {"status": False, "message": "%s" % e.message}
        except Exception, e:
            logger.exception(e)
            return {"status": False, "message": "%s: %s" % (e.__class__.__name__, str(e))}

    @view_config(match_param="action=preview.base64.withmodels")
    def preview_ticket_post64_with_models(self):
        preview = SVGPreviewCommunication.get_instance(self.request)
        svg = self.request.POST["svg"]
        try:
            svg = FillvaluesTransformer(svg, self.request.POST).transform()
            transformer = SVGTransformer(svg, self.request.POST)
            svg = transformer.transform()
            imgdata_base64 = preview.communicate(self.request, svg)
            return {"status": True, "data":imgdata_base64, 
                    "width": transformer.width, "height": transformer.height} #original size
        except TicketPreviewTransformException, e:
            return {"status": False, "message": "%s" % e.message}            
        except TicketPreviewAPIException, e:
            return {"status": False, "message": "%s" % e.message}
        except Exception, e:
            logger.exception(e)
            return {"status": False, "message": "%s: %s" % (e.__class__.__name__, str(e))}


    @view_config(match_param="action=preview.base64.withmodels", request_param="type=sej")
    def preview_ticket_post64_with_models_sej(self):
        preview = SEJPreviewCommunication.get_instance(self.request)
        svg = self.request.POST["svg"]

        try:
            ticket_format_id = self.request.POST["ticket_format"]
            ticket_format = c_models.TicketFormat.query.filter_by(id=ticket_format_id).first()
            if ticket_format is None:
                logger.warn("ticket format %s is not found" % ticket_format_id)
                global_transform = None
            else:
                global_transform = transform_matrix_from_ticket_format(ticket_format)

            svg = FillvaluesTransformer(svg, self.request.POST).transform()
            transformer = SEJTemplateTransformer(svgio=StringIO(svg), global_transform=global_transform)
            ptct = transformer.transform()
            imgdata = preview.communicate(self.request, ptct)
            return {"status": True, "data":base64.b64encode(imgdata), 
                    "width": transformer.width, "height": transformer.height} #original size}
        except TicketPreviewTransformException, e:
            return {"status": False, "message": "%s" % e.message}            
        except TicketPreviewAPIException, e:
            return {"status": False, "message": "%s" % e.message}
        except Exception, e:
            logger.exception(e)
            return {"status": False,  "message": "%s: %s" % (e.__class__.__name__,  str(e))}

    @view_config(match_param="action=collectvars", request_param="svg")
    def preview_collectvars(self):
        svg = self.request.POST["svg"]
        try:
            return {"status": True, "data": list(sorted(template_collect_vars(svg)))}
        except TicketPreviewFillValuesException, e:
            return {"status": False, "message": "%s" % e.message}
        except Exception, e:
            logger.exception(e)
            return {"status": False, "message": "%s: %s" % (e.__class__.__name__, str(e))}


    @view_config(match_param="action=fillvalues", request_param="svg")
    def preview_fillvalues(self):
        svg = self.request.POST["svg"]
        try:
            params = json.loads(self.request.POST["params"])
            dels = []
            for k in params:
                if not params[k]:
                    dels.append(k)
            for k in dels:
                del params[k]
            return {"status": True, "data": template_fillvalues(svg, params)}
        except TicketPreviewFillValuesException, e:
            return {"status": False, "message": "%s" % e.message}
        except Exception, e:
            logger.exception(e)
            return {"status": False, "message": "%s: %s" % (e.__class__.__name__, str(e))}


    @view_config(match_param="action=fillvalues_with_models", request_param="data")
    def preview_fillvalues_with_models(self):
        params = json.loads(self.request.POST["data"])
        v = {}
        try:
            product = params.get("product")
            if product and "pk" in product:
                product = c_models.Product.query.filter_by(id=product["pk"]).first()
                v = build_dict_from_product(product, retval=v)

            performance = params.get("performance")
            event = params.get("event")
            organization = params.get("organization")
            
            if performance and "pk" in performance:
                performance = c_models.Performance.query.filter_by(id=performance["pk"]).first()
                v = build_dict_from_venue(performance.venue, retval=v)
                return {"status": True, "data": decimal_converter(v, converter=float)}
            elif event and "pk" in event:
                event = c_models.Event.query.filter_by(id=event["pk"]).first()
                v = build_dict_from_event(event, retval=v)
                return {"status": True, "data": decimal_converter(v, converter=float)}
            elif organization and "pk" in organization:
                organization = c_models.Organization.query.filter_by(id=organization["pk"]).first()
                v = build_dict_from_organization(organization, retval=v)
                return {"status": True, "data": decimal_converter(v, converter=float)}
            else:
                return {"status": True, "data": decimal_converter(v, converter=float)}
        except Exception, e:
            logger.exception(e)
            return {"status": False, "message": u"補助ダイアログの通信に失敗しました"}


@view_defaults(route_name="tickets.preview.loadsvg.api", request_method="GET", renderer="json", permission="authenticated")
class LoadSVGFromModelApiView(object):
    """
      data = {"svg_resource": {"model_name": "TicketBundle", model: 1}, 
              "fillvalues_resource": {"model_name": "ProductItem", model: 1}}
    """

    def __init__(self, context, request):
        self.context = context 
        self.request = request

    @view_config(match_param="model=ProductItem", request_param="data")
    def svg_from_product_item(self):
        try:
            data = json.loads(self.request.GET["data"])
            ticket_format_id = data["svg_resource"]["model"]
            product_item_id = data["fillvalues_resource"]["model"]

            organization = self.context.organization
            product_item = c_models.ProductItem.query.filter(
                c_models.ProductItem.id==product_item_id,
                c_models.ProductItem.performance_id==c_models.Performance.id, 
                c_models.Performance.event_id==c_models.Event.id, 
                c_models.Event.organization_id==organization.id).first()

            if product_item is None:
                return {"status": False, "message": u"商品が見つかりません。"}
            if data.get("sub_resource"):
                ticket = c_models.Ticket.query.filter(c_models.Ticket.id==data.get("sub_resource")["model"], 
                                                      c_models.Ticket.organization_id==organization.id).first()
            else:
                ticket = c_models.Ticket.query.filter(c_models.TicketBundle.id==product_item.ticket_bundle_id, 
                                                      c_models.Ticket_TicketBundle.ticket_bundle_id==c_models.TicketBundle.id, 
                                                      c_models.Ticket.id==c_models.Ticket_TicketBundle.ticket_id, 
                                                      c_models.Ticket.organization_id==organization.id, 
                                                      c_models.Ticket.ticket_format_id==ticket_format_id).first()
            if ticket is None:
                return {"status": False, "message": u"チケット券面が見つかりません。チケット様式を変更してpreviewを試すか。指定したチケット様式と結びつくチケット券面を作成してください"}
            try:
                svg = template_fillvalues(ticket.drawing, build_dict_from_product_item(product_item))
                return {"status": True, "data": svg}
            except TicketPreviewFillValuesException, e:
                return {"status": False, "message": "%s" % e.message}
        except Exception, e:
            logger.exception(e)
            return {"status": False, "message": str(e)}

    @view_config(match_param="model=Ticket", request_param="data")
    def svg_from_ticket(self):
        try:
            data = json.loads(self.request.GET["data"])
            ticket_id = data["fillvalues_resource"]["model"]
            organization = self.context.organization
            ticket = c_models.Ticket.query.filter_by(id=ticket_id, organization_id=organization.id).first()
            ticket_formats = [_build_ticket_format_dict(ticket.ticket_format)]
            return {"status": True, "data": ticket.drawing, "ticket_formats": ticket_formats}
        except KeyError, e:
            logger.exception(e)
            return {"status": False, "message": str(e)+u"の要素が取得できませんでした".encode("utf-8")}
        except Exception, e:
            logger.exception(e)
            return {"status": False, "message": str(e)}

@view_defaults(route_name="tickets.preview.combobox.api", request_method="GET", renderer="json", permission='sales_counter')
class ComboboxApiView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    result = [{"name": "foo", "pk": 1},{"name": "fooo", "pk": 2},{"name": "foooo", "pk": 3},{"name": "fooooo", "pk": 4},{"name": "foooooooo", "pk": 5}, ]


    @view_config(match_param="model=organization")
    def organization(self):
        o = self.context.organization
        return {"status": True, "data": [{"name": o.name, "pk": o.id}]}


    @view_config(match_param="model=event", request_param="organization")
    def event(self):
        qs = c_models.Event.query.filter(c_models.Event.organization_id==self.request.GET["organization"]) #filter?
        if self.request.GET.get("event_id"):
            qs = qs.filter(c_models.Event.id==self.request.GET.get("event_id"))

        seq = [{"pk": q.id, "name": q.title} for q in qs]
        return {"status": True, "data": seq}


    @view_config(match_param="model=performance", request_param="event")
    def performance(self):
        qs = c_models.Performance.query.filter(c_models.Performance.event_id==self.request.GET["event"], 
                                               c_models.Event.organization_id==self.request.GET["organization"]) #filter?
        if self.request.GET.get("performance_id"):
            qs = qs.filter(c_models.Performance.id==self.request.GET.get("performance_id"))

        qs = qs.options(orm.joinedload(c_models.Performance.venue))
        seq = [{"pk": q.id, "name": u"%s(%s)" % (q.name, q.venue.name)} for q in qs]
        return {"status": True, "data": seq}


    @view_config(match_param="model=product", request_param="performance")
    def product(self):
        qs = c_models.Product.query.filter(c_models.Product.event_id==self.request.GET["event"],
                                           c_models.Product.id==c_models.ProductItem.product_id, 
                                           c_models.ProductItem.performance_id==self.request.GET["performance"])
        ## salessegmentがあるので重複した(name, price)が現れてしまう.nameだけで絞り込み
        seq = {q.name: {"pk": q.id, "name": u"%s(￥%s)" % (q.name, q.price)} for q in qs}
        return {"status": True, "data": sorted(seq.values())}


@view_defaults(route_name="tickets.preview.dialog", request_method="GET", renderer="altair.app.ticketing:templates/tickets/_preview.html", 
               permission="event_editor")
class PreviewWithDefaultParameterDialogView(object):
    def __init__(self, context, request): # as modal dialog
        self.context = context
        self.request = request

    def _combobox_defaults(self):
        get = self.request.GET.get
        combobox_params = dict(organization_id=get("organization_id"), 
                               event_id=get("event_id"), 
                               performance_id=get("performance_id"), 
                               product_id=get("product_id"), 
                               )
        return combobox_params

    def _apis_defaults(self):
        apis = {
            "normalize": self.request.route_path("tickets.preview.api", action="normalize"), 
            "previewbase64": self.request.route_path("tickets.preview.api", action="preview.base64"), 
            "collectvars": self.request.route_path("tickets.preview.api", action="collectvars"), 
            "fillvalues": self.request.route_path("tickets.preview.api", action="fillvalues"), 
            "fillvalues_with_models": self.request.route_path("tickets.preview.api", action="fillvalues_with_models"), 
            }
        return apis


    @view_config(match_param="model=ProductItem")
    def svg_dialog_via_product_item(self):
        try:
            combobox_params = self._combobox_defaults()
            apis = self._apis_defaults()
            apis["loadsvg"]  =  self.request.route_path("tickets.preview.loadsvg.api", model="ProductItem"), 
            apis["combobox"] =  self.request.route_path("tickets.preview.combobox", _query=combobox_params)

            ticket_formats = c_models.TicketFormat.query.filter_by(organization_id=self.context.user.organization_id)
            ticket_formats = _build_ticket_format_dicts(ticket_formats)
            return {"apis": apis, "ticket_formats": ticket_formats}
        except Exception, e:
            logger.exception(e)
            raise

    @view_config(match_param="model=Ticket")
    def svg_dialog_via_ticket(self):
        try:
            combobox_params = self._combobox_defaults()
            apis = self._apis_defaults()
            apis["loadsvg"]  =  self.request.route_path("tickets.preview.loadsvg.api", model="Ticket"), 
            apis["combobox"] =  self.request.route_path("tickets.preview.combobox", _query=combobox_params)

            ticket_formats = c_models.TicketFormat.query.filter_by(organization_id=self.context.user.organization_id)

            if self.request.GET.get("ticket_id"):
                ticket_formats = ticket_formats.filter(c_models.TicketFormat.id==c_models.Ticket.ticket_format_id,
                                                       c_models.Ticket.id==self.request.GET.get("ticket_id"))
            ticket_formats = _build_ticket_format_dicts(ticket_formats)
            return {"apis": apis, "ticket_formats": ticket_formats}
        except Exception, e:
            logger.exception(e)
            raise
