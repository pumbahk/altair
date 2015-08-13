# encoding: utf-8

import logging
from altair.mq.ext import delayed_queue
from altair.mq.decorators import task_config
from altair.sqlahelper import get_db_session
from .interfaces import IFamiPortOrderAutoCompleter
from .autocomplete import FamiPortOrderAutoCompleter, InvalidReceiptStatusError

logger = logging.getLogger(__name__)

class OrderSalvageWorkerResource(object):
    def __init__(self, request):
        self.request = request

@task_config(root_factory=OrderSalvageWorkerResource,
             consumer="famiport",
             name="famiport.salvage_order",
             queue=delayed_queue("famiport.salvage_order", delay=86400000),
             timeout=600)
def salvage_order(context, request):
    try:
        receipt_id_str = request.params['receipt_id']
    except KeyError:
        logger.error('invalid parameters; receipt_id does not exist')
        return

    try:
        receipt_id = long(receipt_id_str)
    except:
        logger.error('invalid receipt_id: %s' % receipt_id_str)

    session = get_db_session(request, 'famiport')
    completer = request.registry.queryUtility(IFamiPortOrderAutoCompleter)
    try:
        completer.complete(session, receipt_id)
    except InvalidReceiptStatusError:
        # 正常系
        pass


def includeme(config):
    config.include('altair.mq')
    config.add_publisher_consumer('famiport', 'altair.ticketing.famiport.mq')
    config.scan(__name__)

def main(global_config, **local_config):
    from pyramid.config import Configurator
    """FamiポートAPIサーバのエントリーポイント"""
    settings = dict(global_config)
    settings.update(local_config)

    config = Configurator(settings=settings)
    completer = FamiPortOrderAutoCompleter(config.registry)
    config.registry.registerUtility(completer, IFamiPortOrderAutoCompleter)

    config.include('pyramid_mako')
    config.add_mako_renderer('.txt')
    config.include('altair.exclog')
    config.include('altair.sqlahelper')
    config.include('.datainterchange')
    config.include('.communication')
    config.include(__name__)

    return config.make_wsgi_app()
