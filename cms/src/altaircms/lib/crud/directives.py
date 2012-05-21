from .views import SimpleCRUDFactory

def add_crud(config, prefix, title=None, model=None, form=None, mapper=None):
    model = config.maybe_dotted(model)
    form = config.maybe_dotted(form)
    mapper = config.maybe_dotted(mapper)
    factory = SimpleCRUDFactory(prefix, title, model, form, mapper)
    factory.bind(config)
