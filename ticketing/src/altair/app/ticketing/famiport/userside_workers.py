# encoding: utf-8

import logging
from pyramid.decorator import reify
from altair.mq.decorators import task_config

from altair.app.ticketing.core.models import Event, FamiPortTenant
from .userside_models import AltairFamiPortPerformanceGroup, AltairFamiPortPerformance, AltairFamiPortSalesSegmentPair

logger = logging.getLogger(__name__)

class SubmissionWorkerResource(object):
    def __init__(self, request):
        self.request = request

@task_config(root_factory=SubmissionWorkerResource,
             consumer="userside_famiport.submit_to_downstream",
             queue="userside_famiport.submit_to_downstream",
             timeout=600)
def submit_to_downstream(context, request):
    from .userside_api import submit_to_downstream_sync
    from altair.app.ticketing.models import DBSession as session
    event = session.query(Event).filter_by(id=request.params['event_id']).one()
    tenant = session.query(FamiPortTenant).filter_by(organization_id=event.organization.id).one()
    submit_to_downstream_sync(request, session, tenant, event)

def includeme(config):
    config.add_publisher_consumer('userside_famiport.submit_to_downstream', 'altair.ticketing.userside_famiport.mq')

