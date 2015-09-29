# -*- coding:utf-8 -*-

from decimal import Decimal
import json
import re
import base64
import os.path
from io import (
    BytesIO,
    StringIO,
    )
from collections import OrderedDict
import sqlalchemy as sa
import sqlalchemy.orm as orm
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from jsonrpclib import jsonrpc
from pyramid.httpexceptions import HTTPBadRequest
import numpy
from PIL import Image as image
from altair.pyramid_assets.api import get_asset_resolver
from altair.app.ticketing.payments.api import get_delivery_plugin
from altair.app.ticketing.payments.interfaces import ISejDeliveryPlugin
from altair.app.ticketing.payments.plugins import(
    SEJ_DELIVERY_PLUGIN_ID,
    FAMIPORT_DELIVERY_PLUGIN_ID,
    QR_DELIVERY_PLUGIN_ID,
    ORION_DELIVERY_PLUGIN_ID,
    RESERVE_NUMBER_DELIVERY_PLUGIN_ID,
    SHIPPING_DELIVERY_PLUGIN_ID
)
INENR_DELIVERY_PLUGIN_ID_LIST = [
    SHIPPING_DELIVERY_PLUGIN_ID,
    RESERVE_NUMBER_DELIVERY_PLUGIN_ID,
    QR_DELIVERY_PLUGIN_ID,
    ORION_DELIVERY_PLUGIN_ID,
]

from altair.app.ticketing.core.modelmanage import ApplicableTicketsProducer
import logging
logger = logging.getLogger(__name__)

from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.tickets.utils import (
    transform_matrix_from_ticket_format,
    build_dict_from_product,
    build_dict_from_venue,
    build_dict_from_event,
    build_dict_from_organization,
)

from .api import (
    SVGPreviewCommunication,
    SEJPreviewCommunication,
    as_filelike_response
)
from .transform import (
    SVGTransformer,
    FillvaluesTransformer,
    SEJTemplateTransformer
)

from .fillvalues import (
    template_collect_vars,
    template_fillvalues,
    natural_order
)
from .fetchsvg import fetch_svg_from_postdata
from ..cleaner.api import get_validated_svg_cleaner
from altair.response import (
    FileLikeResponse,
    ZipFileResponse,
    ZipFileCreateRecursiveWalk
)

# todo: refactoring
from ..utils import build_dict_from_product_item
from altair.svg.geometry import parse_transform

from . import TicketPreviewAPIException
from . import TicketPreviewTransformException
from . import TicketPreviewFillValuesException
from ..cleaner.api import TicketCleanerValidationError
import tempfile


regx_xmldecl = re.compile('<\?xml.*?\?>', re.I)  # XML宣言にマッチする (例) '<?xml version="1.0" ?>'


sej_ticket_printer_transforms = {
    'old': numpy.matrix(
        [
            [1., 0., -63.0708], # 17.8mm in 90dpi
            [0., 1., -10.6299], # 3mm in 90dpi
            [0., 0., 1.     ]
            ],
        dtype=numpy.float64
        ),
    'new': numpy.matrix(
        [
            [1., 0., -71.2204], # 20.1mm in 90dpi
            [0., 1., -23.0314], # 6.5mm in 90dpi
            [0., 0., 1.     ]
            ],
        dtype=numpy.float64
        )
    }

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

def _build_selectitem_candidates_from_ticket_format_query(ticket_format_qs):
    sej_qs = ticket_format_qs.filter(
        c_models.TicketFormat.id==c_models.TicketFormat_DeliveryMethod.ticket_format_id,
        c_models.TicketFormat_DeliveryMethod.delivery_method_id==c_models.DeliveryMethod.id, 
        c_models.DeliveryMethod.delivery_plugin_id==SEJ_DELIVERY_PLUGIN_ID)
    qs = ticket_format_qs.filter(
        c_models.TicketFormat.id==c_models.TicketFormat_DeliveryMethod.ticket_format_id,
        c_models.TicketFormat_DeliveryMethod.delivery_method_id==c_models.DeliveryMethod.id, 
        c_models.DeliveryMethod.delivery_plugin_id!=SEJ_DELIVERY_PLUGIN_ID).distinct(c_models.TicketFormat.id)

    D = {}
    for t in qs:
        D[(t.id, "")] = {"name": t.name, "type": ""}
    for t in sej_qs:
        D[(t.id, "sej")] = {"name": t.name, "type": "sej"}
    return [dict(pk=k, **vs) 
            for (k, _), vs in D.iteritems()]

def _build_selectitem_candidates_from_ticket_format_unit(ticket_format, is_sej):
    sej_value = None
    normal_value = None
    for dm in ticket_format.delivery_methods:
        if int(dm.delivery_plugin_id) == int(SEJ_DELIVERY_PLUGIN_ID):
            sej_value = {"pk": ticket_format.id, "name": ticket_format.name, "type": "sej"}
        else:
            normal_value = {"pk": ticket_format.id, "name": ticket_format.name, "type": ""}
    if is_sej:
        return [e for e in [sej_value, normal_value] if e is not None]
    else:
        return [e for e in [normal_value, sej_value] if e is not None]


def validate_and_filter_image_location(im_loc):
    if im_loc is None:
        return None
    s = []
    for c in re.split(ur'/+', im_loc):
        if c == u'..':
            if len(s) == 0:
                raise ValueError('invalid virtual path; could not go back beyond the root')
            s.pop()
        elif c != u'' and c != u'.':
            s.append(c)
    return u'/'.join(s)

def load_ticket_image(request, ticket_format):
    im_loc = ticket_format.data.get('ticket_image')
    im_loc = validate_and_filter_image_location(im_loc)
    if im_loc is None:
        return None
    resolver = get_asset_resolver(request)
    desc = resolver.resolve('altair.app.ticketing:static/images/tickets/%s' % im_loc)
    return image.open(desc.stream())

def composite_ticket_image(request, ticket_format, im, im_info_defaults={'dpi':(300, 300)}, ticket_im_info_defaults={'dpi':(90, 90)}):
    try:
        ticket_im = load_ticket_image(request, ticket_format)
    except Exception as e:
        logger.warn(e)
        return im
    if ticket_im is None:
        logger.info('no image specified')
        return im
    im_info = dict(im_info_defaults)
    im_info.update(im.info)
    ticket_im_info = dict(ticket_im_info_defaults)
    ticket_im_info.update(ticket_im.info)
    im_dpi = im_info['dpi']
    ticket_im_dpi = ticket_im_info['dpi']
    if ticket_im_dpi[0] != im_dpi[0] or ticket_im_dpi[1] != im_dpi[1]:
        ticket_im = ticket_im.resize(
            (
                int(ticket_im.size[0] * float(im_dpi[0]) / float(ticket_im_dpi[0])),
                int(ticket_im.size[1] * float(im_dpi[1]) / float(ticket_im_dpi[1]))
                ),
            image.ANTIALIAS
            )
    sej_ticket_printer_type = None
    aux = ticket_format.data.get('aux')
    if aux is not None:
        sej_ticket_printer_type = aux.get('sej_ticket_printer_type')
    trans = None
    if sej_ticket_printer_type is not None:
        trans = sej_ticket_printer_transforms.get(sej_ticket_printer_type)
        if trans is None:
            logger.warning('unknown SEJ ticket printer type: %s' % sej_ticket_printer_type)
        trans = trans.copy() # matrix will be modified later in place.
    else:
        logger.info('aux.sej_ticket_printer_type is not specified')
    if trans is None:
        trans = transform_matrix_from_ticket_format(ticket_format)
    trans[0, 2] *= float(im_dpi[0]) / 90.
    trans[1, 2] *= float(im_dpi[1]) / 90.
    im = im.transform(
        ticket_im.size,
        image.AFFINE,
        tuple(trans[0:2].getA().flatten()),
        image.NEAREST
        )
    return image.composite(im, ticket_im, im)

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
    ticket_formats = c_models.TicketFormat.query.filter_by(organization_id=context.organization.id)
    ticket_formats = _build_selectitem_candidates_from_ticket_format_query(ticket_formats)
    return {"apis": apis, "ticket_formats": ticket_formats}


@view_config(route_name="tickets.preview", request_method="POST", permission='sales_counter')
def preview_ticket_post(context, request):
    """
    curl -Fsvgfile=@<file> <url> > out.png
    """
    preview = SVGPreviewCommunication.get_instance(request)
    ticket_format = c_models.TicketFormat.query \
        .filter(c_models.TicketFormat.organization_id == context.organization.id) \
        .filter(c_models.TicketFormat.id == request.POST["ticket_format"]) \
        .one()
    if "raw" in request.POST:
        svg_string = request.POST["svgfile"].file.read()
    else:
        svgio = request.POST["svgfile"].file 
        cleaner = get_validated_svg_cleaner(svgio, exc_class=HTTPBadRequest)
        svgio = cleaner.get_cleaned_svgio()
        svg_string = svgio.getvalue()
    try:
        imgdata_base64 = preview.communicate(request, svg_string, ticket_format)
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

    ticket_format = c_models.TicketFormat.query \
        .filter(c_models.TicketFormat.organization_id == context.organization.id) \
        .filter(c_models.TicketFormat.id == request.POST["ticket_format"]) \
        .one()

    delivery_plugin = get_delivery_plugin(request, SEJ_DELIVERY_PLUGIN_ID)
    assert ISejDeliveryPlugin.providedBy(delivery_plugin)
    template_record = delivery_plugin.template_record_for_ticket_format(request, ticket_format)
    transformer = SEJTemplateTransformer(
        svgio=svgio,
        global_transform=transform,
        notation_version=template_record.notation_version
        )
    ptct = transformer.transform()
    imgdata = preview.communicate(request, (ptct, template_record), ticket_format)
    return as_filelike_response(request, imgdata)


@view_config(route_name="tickets.preview.download", request_method="POST", permission='sales_counter', request_param="svg")
def preview_ticket_download(context, request):
    io = BytesIO(request.POST["svg"].encode("utf-8"))
    return FileLikeResponse(io, request=request, filename="preview.svg")


@view_config(route_name="tickets.preview.enqueue", request_method="POST", permission='sales_counter', request_param="svg", renderer="json")
def ticket_preview_enqueue(context, request):
    svg = request.POST["svg"]
    ticket_format_id = request.POST["ticket_format_id"] # これが ticket_format_id になってしまっているのは歴史的経緯
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
            svgio = BytesIO(unicode(self.request.POST["svg"]).encode("utf-8"))  # unicode only
            cleaner = get_validated_svg_cleaner(svgio, exc_class=Exception)
            svgio = cleaner.get_cleaned_svgio()
            return {"status": True, "data": svgio.getvalue()}
        except TicketCleanerValidationError, e:
            return {"status": False, "message": e.message}
        except Exception, e:
            logger.exception(e)
            return {"status": False, "message": "%s: %s" % (e.__class__.__name__, str(e))}

    @view_config(match_param="action=identity", request_param="svg")
    def preview_api_identity(self):
        return {"status": True, "data": self.request.POST["svg"]}

    @view_config(match_param="action=preview.base64")
    def preview_ticket_post64(self):
        preview = SVGPreviewCommunication.get_instance(self.request)
        try:
            svg = self.request.POST["svg"]
            ticket_format = c_models.TicketFormat.query \
                .filter(c_models.TicketFormat.organization_id == self.context.organization.id) \
                .filter(c_models.TicketFormat.id == self.request.POST["ticket_format"]) \
                .one()
            transformer = SVGTransformer(svg, self.request.POST)
            svg = transformer.transform()
            imgdata_base64 = preview.communicate(self.request, svg, ticket_format)
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
        without_ticket_image = self.request.params.get('without_ticket_image', False)
        try:
            ticket_format = c_models.TicketFormat.query \
                .filter(c_models.TicketFormat.organization_id == self.context.organization.id) \
                .filter(c_models.TicketFormat.id == self.request.POST["ticket_format"]) \
                .one()
            preview = SEJPreviewCommunication.get_instance(self.request)
            global_transform = transform_matrix_from_ticket_format(ticket_format)
            delivery_plugin = get_delivery_plugin(self.request, SEJ_DELIVERY_PLUGIN_ID)
            assert ISejDeliveryPlugin.providedBy(delivery_plugin)
            template_record = delivery_plugin.template_record_for_ticket_format(self.request, ticket_format)
            transformer = SEJTemplateTransformer(
                svgio=BytesIO(self.request.POST["svg"].encode('utf-8')),
                global_transform=global_transform,
                notation_version=template_record.notation_version
                )
            ptct = transformer.transform()
            imgdata = preview.communicate(self.request, (ptct, template_record), ticket_format)
            if not without_ticket_image:
                f = BytesIO(imgdata)
                f.name = 'svg.png'
                im = composite_ticket_image(self.request, ticket_format, image.open(f), im_info_defaults={'dpi':(300, 300)})
                f = BytesIO()
                im.save(f, 'png')
                imgdata = f.getvalue()
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

    @view_config(match_param="action=preview.base64", request_param="type=famiport") #svg
    def preview_ticket_post64_famiport(self):
        # todo:本来famiport preview serverと通信して券面画像取得するようにすべき
        preview = SVGPreviewCommunication.get_instance(self.request)
        try:
            svg = self.request.POST["svg"]
            ticket_format = c_models.TicketFormat.query \
                .filter(c_models.TicketFormat.organization_id == self.context.organization.id) \
                .filter(c_models.TicketFormat.id == self.request.POST["ticket_format"]) \
                .one()
            transformer = SVGTransformer(svg, self.request.POST)
            svg = transformer.transform()
            imgdata_base64 = preview.communicate(self.request, svg, ticket_format)
            f = BytesIO(base64.decodestring(imgdata_base64))
            imgdata = image.open(f)
            im = composite_ticket_image(self.request, ticket_format, imgdata, im_info_defaults={'dpi':(300, 300)})
            f = BytesIO()
            im.save(f, 'png')
            imgdata = f.getvalue()
            return {"status": True, "data":base64.b64encode(imgdata),
                    "width": transformer.width, "height": transformer.height} #original size
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
        try:
            svg = self.request.POST["svg"]
            ticket_format = c_models.TicketFormat.query \
                .filter(c_models.TicketFormat.organization_id == self.context.organization.id) \
                .filter(c_models.TicketFormat.id == self.request.POST["ticket_format"]) \
                .one()
            svg = FillvaluesTransformer(svg, self.request.POST).transform()
            transformer = SVGTransformer(svg, self.request.POST)
            svg = transformer.transform()
            imgdata_base64 = preview.communicate(self.request, svg, ticket_format)
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
        try:
            svg = self.request.POST["svg"]
            ticket_format = c_models.TicketFormat.query \
                .filter(c_models.TicketFormat.organization_id == self.context.organization.id) \
                .filter(c_models.TicketFormat.id == self.request.POST["ticket_format"]) \
                .one()
            global_transform = transform_matrix_from_ticket_format(ticket_format)
            svg = FillvaluesTransformer(svg, self.request.POST).transform()
            delivery_plugin = get_delivery_plugin(self.request, SEJ_DELIVERY_PLUGIN_ID)
            assert ISejDeliveryPlugin.providedBy(delivery_plugin)
            template_record = delivery_plugin.template_record_for_ticket_format(self.request, ticket_format)
            transformer = SEJTemplateTransformer(
                svgio=BytesIO(svg),
                global_transform=global_transform,
                notation_version=template_record.notation_version
                )
            ptct = transformer.transform()
            imgdata = preview.communicate(self.request, (ptct, template_record), ticket_format)
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
            return {"status": True, "data": natural_order(template_collect_vars(svg))}
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
            current_preview_type = data["svg_resource"].get("type")
            organization = self.context.organization
            ticket = c_models.Ticket.query.filter_by(id=ticket_id, organization_id=organization.id).first()
            ticket_formats = _build_selectitem_candidates_from_ticket_format_unit(ticket.ticket_format, current_preview_type == "sej")
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
            if "event_id" in self.request.GET:
                bundles = c_models.TicketBundle.query.filter(c_models.TicketBundle.event_id == self.request.GET.get("event_id")).all()
                D = OrderedDict()
                for b in bundles:
                    for t in ApplicableTicketsProducer(b).will_issued_by_own_tickets(delivery_plugin_ids=INENR_DELIVERY_PLUGIN_ID_LIST): #xxx: ApplicableTicketsProducer.will_issued_by_own_ticketsはsejと紐つくとダメ。
                        tf = t.ticket_format
                        D[(tf.id, "")] = {"pk": tf.id, "name": tf.name, "type": ""}
                for b in bundles:
                    for t in ApplicableTicketsProducer(b).sej_only_tickets():
                        tf = t.ticket_format
                        D[(tf.id, "sej")] = {"pk": tf.id, "name": tf.name, "type": "sej"}
                for b in bundles:
                    for t in ApplicableTicketsProducer(b).famiport_only_tickets():
                        tf = t.ticket_format
                        D[(tf.id, "famiport")] = {"pk": tf.id, "name": tf.name, "type": "famiport"}
                ticket_formats = D.values()
            else:
                ticket_formats = c_models.TicketFormat.query.filter_by(organization_id=self.context.user.organization_id)
                ticket_formats = _build_selectitem_candidates_from_ticket_format_query(ticket_formats)
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
            ticket_formats = _build_selectitem_candidates_from_ticket_format_query(ticket_formats)
            return {"apis": apis, "ticket_formats": ticket_formats}
        except Exception, e:
            logger.exception(e)
            raise

class DownloadListOfPreviewImage(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name="tickets.preview.download.list.zip")
    def __call__(self):
        performance_id = self.request.matchdict["performance_id"]
        sales_segment_id = self.request.matchdict["sales_segment_id"]
        try:
            delivery_method_id = self.request.params["delivery_method_id"]
        except KeyError:
            logger.warn("delivery method not found")
            raise HTTPNotFound("delivery_method not found")
        ticket_format = c_models.TicketFormat.query \
            .filter(c_models.TicketFormat.organization_id == self.context.organization.id) \
            .filter(c_models.TicketFormat.id == self.request.params["ticket_format_id"]) \
            .one()

        self.assertion(performance_id, self.context.organization)

        q = self.model_query(performance_id, sales_segment_id)

        ## ProductItem list -> svg list
        svg_string_list = self.fetch_data_list(q, self.context.organization, unicode(delivery_method_id), ticket_format)

        source_dir = tempfile.mkdtemp()
        try:
            ## preview serverと通信して取得した画像を保存
            self.store_image(svg_string_list, source_dir, ticket_format)
        except jsonrpc.ProtocolError, e:
            raise HTTPBadRequest(str(e))

        ## zipfile作成
        zip_name = "preview_image_salessegment{0}.zip".format(sales_segment_id)
        walk = self.create_zip_file_creator(tempfile.mktemp(zip_name), source_dir)
        return ZipFileResponse(walk, filename=zip_name)


    def create_zip_file_creator(self, zip_path, source_dir):
        walk = ZipFileCreateRecursiveWalk(zip_path, source_dir, flatten=True)
        return walk

    def assertion(self, performance_id, organization):
        p = c_models.Performance.query.filter_by(id=performance_id).one()
        if unicode(p.event.organization_id) != unicode(organization.id):
            logger.warn("unmatched organization %s != %s", p.event.organization, organization.id)
            raise HTTPFound("unmatched organization")


    def model_query(self, performance_id, sales_segment_id):
        return (c_models.ProductItem.query
                .filter(c_models.Product.id==c_models.ProductItem.product_id)
                .filter(c_models.Product.sales_segment_id==sales_segment_id)
                .filter(c_models.Product.performance_id==performance_id)
                .filter(c_models.ProductItem.performance_id==performance_id)
                .order_by(sa.asc(c_models.Product.display_order))
                .all())

    def fetch_data_list(self, q, organization, delivery_method_id, ticket_format):
        svg_string_list = []
        dm = c_models.DeliveryMethod.query.filter_by(id=delivery_method_id).one()
        for product_item in q:
            ticket_q = (c_models.Ticket.query
                        .filter(c_models.TicketBundle.id==product_item.ticket_bundle_id,
                                c_models.Ticket_TicketBundle.ticket_bundle_id==product_item.ticket_bundle_id,
                                c_models.Ticket.id==c_models.Ticket_TicketBundle.ticket_id,
                                c_models.Ticket.ticket_format==ticket_format,
                                c_models.Ticket.organization_id==organization.id)
                        .all())
            for ticket in ticket_q:
                if not any(unicode(dm.id) == delivery_method_id for dm in ticket.ticket_format.delivery_methods):
                    continue
                svg = template_fillvalues(ticket.drawing, build_dict_from_product_item(product_item))
                if str(dm.delivery_plugin_id) == str(SEJ_DELIVERY_PLUGIN_ID):
                    global_transform = transform_matrix_from_ticket_format(ticket.ticket_format)
                    delivery_plugin = get_delivery_plugin(self.request, SEJ_DELIVERY_PLUGIN_ID)
                    assert ISejDeliveryPlugin.providedBy(delivery_plugin)
                    template_record = delivery_plugin.template_record_for_ticket_format(self.request, ticket_format)
                    svgio = StringIO(regx_xmldecl.sub('', svg))
                    transformer = SEJTemplateTransformer(
                        svgio=svgio,
                        global_transform=global_transform,
                        notation_version=template_record.notation_version
                        )
                    ptct = transformer.transform()
                    svg_string_list.append(((ptct, template_record), product_item, ticket, "sej"))
                else:
                    transformer = SVGTransformer(svg)
                    transformer.data["ticket_format"] = ticket.ticket_format
                    svg = transformer.transform()
                    svg_string_list.append((svg, product_item, ticket, "default"))
        return svg_string_list

    def store_image(self, svg_string_list, source_dir, ticket_format):
        preview_default = SVGPreviewCommunication.get_instance(self.request)
        preview_sej = SEJPreviewCommunication.get_instance(self.request)
        ## 画像取得
        with open(os.path.join(source_dir, "memo.txt"), "w") as wf0:
            for i, (svg_string, product_item, ticket, preview_type) in enumerate(svg_string_list):
                wf0.write(u"* preview{0}.png -- 商品:{1}\n".format(i, product_item.name).encode("utf-8"))
                if preview_type == "sej":
                    imgdata = preview_sej.communicate(self.request, svg_string, ticket_format)
                    fname = os.path.join(source_dir, "preview{0}.png".format(i))
                    logger.info("writing .. preview_type=sej ... %s", fname)
                    with open(fname, "wb") as wf:
                        wf.write(imgdata)
                else:
                    imgdata_base64 = preview_default.communicate(self.request, svg_string, ticket_format)
                    fname = os.path.join(source_dir, "preview{0}.png".format(i))
                    logger.info("writing .. preview_type=default ... %s", fname)
                    with open(fname, "wb") as wf:
                        wf.write(base64.b64decode(imgdata_base64))
