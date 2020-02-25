import logging
from pyramid_mailer.message import Message
from pyramid_mailer import get_mailer

logger = logging.getLogger(__file__)

def _send_mail(request, title, body, recipients):
    mailer = get_mailer(request)
    message = Message(subject=title,
                      sender=request.sender_mailaddress,
                      recipients=recipients,
                      body=body)
    mailer.send(message)

def send_inquiry_mail(request, title, body, recipients):
    ret = True
    try:
        _send_mail(request=request, title=title, body=body, recipients=recipients)
    except Exception as e:
        ret = False
    return ret
