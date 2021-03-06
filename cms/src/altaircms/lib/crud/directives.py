from .views import SimpleCRUDFactory
import logging
logger = logging.getLogger(__file__)

def add_crud(config, prefix, title=None, model=None, form=None, mapper=None, bind_actions=None, filter_form=None, events=None, 
             has_auto_generated_permission=True, endpoint=None, circle_type="circle-master",  override_templates=None, **default_kwargs):
    bind_actions = bind_actions or ["create", "update", "delete", "list"]
    logger.debug("crud: auto generate view route = %s" % [u"%s_%s" % (prefix, a)for a in bind_actions])

    model = config.maybe_dotted(model)
    form = config.maybe_dotted(form)
    mapper = config.maybe_dotted(mapper)
    filter_form = config.maybe_dotted(filter_form)
    factory = SimpleCRUDFactory(prefix, title, model, form, mapper, filter_form=filter_form)
    factory.bind(config, bind_actions, events=events,endpoint=endpoint, 
                 has_auto_generated_permission=has_auto_generated_permission, 
                 circle_type=circle_type, 
                 override_templates=override_templates, 
                 **default_kwargs)
    return factory
