##
## API views
##
import collections

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, HTTPCreated, HTTPOk

from altaircms.views import BaseRESTAPI
from altaircms.fanstatic import with_bootstrap

from . import mappers
from . import forms
from altaircms import models

class TopicRESTAPIView(BaseRESTAPI):
    model = models.Topic
    form = forms.TopicForm
    object_mapper = mappers.TopicMapper
    objects_mapper = mappers.TopicsMapper

    @view_config(route_name='api_topic', request_method='PUT')
    def create(self):
        (created, object, errors) = super(TopicRESTAPIView, self).create()
        return HTTPCreated() if created else HTTPBadRequest(errors)

    @view_config(route_name='api_topic', request_method='GET', renderer='json')
    @view_config(route_name='api_topic_object', request_method='GET', renderer='json')
    def read(self):
        resp = super(TopicRESTAPIView, self).read()
        if isinstance(resp, collections.Iterable):
            return self.objects_mapper({'topics': resp}).as_dict()
        else:
            return self.object_mapper(resp).as_dict()

    @view_config(route_name='api_topic_object', request_method='PUT')
    def update(self):
        status = super(TopicRESTAPIView, self).update()
        return HTTPOk() if status else HTTPBadRequest()

    @view_config(route_name='api_topic_object', request_method='DELETE')
    def delete(self):
        status = super(TopicRESTAPIView, self).delete()
        return HTTPOk() if status else HTTPBadRequest()

@view_config(route_name='topic', renderer='altaircms:templates/topic/view.mako', permission='topic_read',
             decorator=with_bootstrap)
def view(request):
    id_ = request.matchdict['id']

    topic = TopicRESTAPIView(request, id_).read()
    pages = DBSession.query(Page).filter_by(topic_id=topic['id'])
    performances = DBSession.query(Performance).filter(Performance.topic_id==topic["id"])
    return dict(
        topic=topic,
        pages=pages, 
        performances=performances
    )

##
## CMS view
##



@view_config(route_name='topic_list', renderer='altaircms:templates/topic/list.mako', permission='topic_create', request_method="POST", 
             decorator=with_bootstrap)
def _post_list_(request):
    topics = TopicRESTAPIView(request).read()
    form = forms.TopicForm(request.POST)
    if form.validate():
        request.method = "PUT"
        TopicRESTAPIView(request).create()
        return HTTPFound(request.route_url("topic_list"))

    return dict(
        form=form,
        topics=topics
    )

@view_config(route_name='topic_list', renderer='altaircms:templates/topic/list.mako', permission='topic_read', request_method="GET", 
             decorator=with_bootstrap)
def _get_list_(request):
    topics = TopicRESTAPIView(request).read()
    form = forms.TopicForm()
    return dict(
        form=form,
        topics=topics
    )
