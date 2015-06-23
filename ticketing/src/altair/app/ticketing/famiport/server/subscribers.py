from pyramid.events import subscriber
from altair.mq import get_publisher
from urllib import urlencode
from ..interfaces import IReceiptPaymentRequestReceived

@subscriber(IReceiptPaymentRequestReceived)
def submit_to_autocomplete_queue(event):
    request = event.request
    famiport_receipt = event.famiport_receipt
    publisher = get_publisher(request, 'famiport.salvage_order')
    publisher.publish(
        routing_key='famiport.salvage_order',
        body=urlencode({ 'receipt_id': famiport_receipt.id }),
        properties={'content_type': 'application/x-www-form-urlencoded'}
        )

def includeme(config):
    config.scan(__name__)
