from .views import SimpleCRUDViewFactory

def add_crud(config, prefix, title=None, model=None, form=None):
    model = config.maybe_dotted(model)
    form = config.maybe_dotted(form)
    factory = SimpleCRUDViewFactory(prefix, title, model, form)
    factory.generate(config)
