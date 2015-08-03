import logging
from zope.interface import implementer
from urllib2 import Request
from lxml import etree, builder
from base64 import b64decode
from .interfaces import IFamiPortTicketPreviewAPI
from .utils import FamiPortCrypt

logger = logging.getLogger(__name__)

@implementer(IFamiPortTicketPreviewAPI)
class FamiPortTicketPreviewAPI(object):
    def __init__(self, opener, endpoint_url):
        self.opener = opener
        self.endpoint_url = endpoint_url

    def build_payload(self, request, discrimination_code, client_code, order_id, barcode_no, name, member_id, address_1, address_2, identify_no, tickets, response_image_type):
        if response_image_type == 'pdf':
            response_image_type = u'1'
        elif response_image_type == 'jpeg':
            response_image_type = u'2'
        c = FamiPortCrypt(order_id)
        E = builder.E
        request_body = '<?xml version="1.0" encoding="Shift_JIS" ?>' + \
            etree.tostring(
                E.FMIF(
                    E.playGuideCode(discrimination_code.zfill(2)),
                    E.clientId(client_code.zfill(24)),
                    E.barCodeNo(barcode_no),
                    E.orderId(order_id),
                    E.name(c.encrypt(name) if name else u''),
                    E.memberId(c.encrypt(member_id) if member_id else u''),
                    E.address1(c.encrypt(address_1) if address_1 else u''),
                    E.address2(c.encrypt(address_2) if address_2 else u''),
                    E.identifyNo(identify_no if identify_no else u''),
                    E.responseImageType(response_image_type),
                    *(
                        E.ticket(
                            E.barCodeNo(ticket['barcode_no']),
                            E.templateCode(ticket['template_code']),
                            E.ticketData('<?xml version="1.0" encoding="Shift_JIS" ?>' + ticket['data'])
                            )
                        for ticket in tickets
                        )
                    ),
                encoding='unicode'
                ).encode('CP932')
        return request_body

    def __call__(self, request, discrimination_code, client_code, order_id, barcode_no, name, member_id, address_1, address_2, identify_no, tickets, response_image_type):
        logger.info('sending request to %s' % self.endpoint_url)
        request_body = self.build_payload(request, discrimination_code, client_code, order_id, barcode_no, name, member_id, address_1, address_2, identify_no, tickets, response_image_type)
        request = Request(self.endpoint_url, request_body, headers={'Content-Type': 'application/xml; charset=Shift_JIS'})
        response = self.opener.open(request)
        xml = etree.parse(response)
        result_code_node = xml.find('resultCode')
        if result_code_node is None:
            raise FDCAPIError('invalid response')
        if result_code_node.text != u'00':
            raise FDCAPIError('server returned error status (%s)' % result_code_node.text)
        return [
            b64decode(encoded_ticket_preview_pictures.text.replace(u' ', u'+').replace(u'-', u'/'))
            for encoded_ticket_preview_pictures in xml.findall('kenmenImage')
            ]


