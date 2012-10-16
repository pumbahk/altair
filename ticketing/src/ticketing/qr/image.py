import qrcode
import StringIO
from pyramid.response import Response

def make_qrimage_from_qrdata(ticket):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        )
    qr.add_data(ticket.qr)
    qr.make(fit=True)
    return qr.make_image()

def qrimage_as_response(img):
    r = Response(status=200, content_type="image/png")
    buf = StringIO.StringIO()
    img.save(buf, 'PNG')
    r.body = buf.getvalue()
    return r

def qrdata_as_image_response(qrdata):
    return qrimage_as_response(make_qrimage_from_qrdata(qrdata))
