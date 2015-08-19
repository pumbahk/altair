import logging
from pyramid.config import ConfigurationError
from pyramid.events import subscriber
from altair.mq import dispatch_task
from altair.timeparse import parse_time_spec
from urllib import urlencode
from ..interfaces import IReceiptPaymentRequestReceived

logger = logging.getLogger(__name__)

class AutoCompleteQueueSubmitter(object):
    def __init__(self, registry):
        v_str = registry.settings.get('altair.famiport.auto_complete_time', None)
        if v_str is None:
            logger.warning('altair.famiport.auto_complete_time is missing. defaults to 90 minutes')
            v_str = '90 minutes'
        v = parse_time_spec(v_str)
        if v is None:
            raise ConfigurationError('invalid value for altair.famiport.auto_complete_time: %s' % v_str)
        logger.info('auto_complete time: %r' % v)
        self.delay = v

    def __call__(self, event):
        request = event.request
        famiport_receipt = event.famiport_receipt
        publisher = dispatch_task(
            request,
            consumer_name='famiport',
            task_name='famiport.salvage_order',
            body={ 'receipt_id': famiport_receipt.id },
            properties={
                'expiration': '%d' % (self.delay.seconds * 1000),
                }
            )

def includeme(config):
    config.add_subscriber(
        AutoCompleteQueueSubmitter(config.registry),
        IReceiptPaymentRequestReceived
        )
