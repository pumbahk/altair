# encoding: utf-8

import sys
import logging
from base64 import b64encode
from pyramid.config import Configurator
from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
from lxml import etree
from io import BytesIO
from PIL.Image import new as new_image
from PIL.ImageDraw import Draw as Draw
from PIL.ImageFont import truetype
from .comm import CommunicationError, parse_response

logger = logging.getLogger(__name__)

fonts = {
    'darwin': u'/System/Library/Fonts/ヒラギノ角ゴ ProN W3.otf', 
    'winnt': u'C:\\Windows\\Fonts\\msgothic.ttc',
    'linux2': u'/usr/share/fonts/truetype/fonts-japanese-gothic.ttf',
    }

class BaseResource(object):
    def __init__(self, request):
        self.request = request


def draw_text_with_wrapping(d, pos, size, text, font, fill):
    w, h = size
    tw, th  = d.textsize(text, font=font)
    x = 0
    y = th
    i = 0
    approximate_characters_per_line = int(float(w) / (float(tw) / len(text)))

    while i < len(text):
        lb = text[i:].find(u'\n')
        if lb < 0:
            lb = len(text)
        else:
            lb = i + lb
        e = i + 1
        if i + approximate_characters_per_line > lb + 1:
            for e in range(lb, i, -1):
                tw, th = d.textsize(text[i:e], font=font)
                if tw < w:
                    break
        else:
            e = lb
            for e in range(i + approximate_characters_per_line, lb + 1):
                tw, th = d.textsize(text[i:e], font=font)
                if tw > w:
                    e -= 1
                    break
        if e < i:
            raise RuntimeError()
        d.text((x + pos[0], y + pos[1]), text[i:e], font=font, fill=fill)
        i = e
        if i == lb:
            # skip the line break character
            i += 1
        y += th

@view_config(route_name='preview', request_method='GET')
def preview_get(context, request):
    return Response(text=u'???')

@view_config(route_name='preview', request_method='POST')
def preview(context, request):
    if request.content_type not in ('text/xml', 'application/xml'):
        logger.error('invalid content type: %s' % request.content_type)
        raise HTTPBadRequest()
    result_code = u'00'
    images = []
    try:
        req = parse_response(etree.fromstring(request.body))
        tickets = req.get('ticket')
        if tickets is None:
            tickets = []
        elif not isinstance(tickets, list):
            tickets = [tickets]
        if req['responseImageType'] == '1':
            format = 'pdf'
        elif req['responseImageType'] == '2':
            format = 'jpeg'
        else:
            raise CommunicationError('invalid image type')

        barcode_no = req['barCodeNo']
        logger.info('barCodeNo=%(barcode_no)s, len(tickets)=%(num_tickets)d' % dict(barcode_no=barcode_no, num_tickets=len(tickets)))
        for ticket in tickets:
            x = etree.fromstring(ticket['ticketData'].encode('Shift_JIS'))
            text = (u'barcodeNo: %s\n' % ticket['barCodeNo']) + u' '.join([u'%s: %s' % (n.tag, n.text.strip() if n.text is not None else u'') for n in x])
            im = new_image('RGB', (600, 200))
            d = Draw(im)
            d.rectangle(((0, 0), im.size), fill=(255, 255, 255))
            font_file_path = fonts[sys.platform]
            f = truetype(font_file_path, 12)
            draw_text_with_wrapping(d, (0, 0), im.size, text, font=f, fill=(0, 0, 0))
            images.append(im)
    except:
        logger.exception(u'oops')
        result_code = u'99'
    root_n = etree.Element(u'FMIF')
    result_code_n = etree.Element(u'resultCode')
    result_code_n.text = result_code
    root_n.append(result_code_n)
    for image in images:
        image_n = etree.Element(u'kenmenImage')
        f = BytesIO()
        image.save(f, format=format)
        image_n.text = unicode(b64encode(f.getvalue()).replace('+', ' ').replace('/', '-'), 'ASCII')
        root_n.append(image_n)
    return Response(body=etree.tostring(root_n, encoding='Shift_JIS'), content_type='text/xml', charset='Shift_JIS')


def main(global_conf, **local_conf):
    settings = dict(global_conf)
    settings.update(local_conf)
    config = Configurator(settings=settings)
    config.include('altair.exclog')
    config.set_root_factory(BaseResource)
    config.add_route('preview', '/')
    config.scan(__name__)
    return config.make_wsgi_app()
