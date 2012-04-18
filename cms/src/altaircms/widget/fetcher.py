import logging

class WidgetFetchException(Exception):
    pass

class WidgetFetcher(object):
    """ fetching a widget from a element of page.structure .
    e.g. {block_name: "image_widget",  pk: 1} => <ImageWidget object>
    """
    def __init__(self, session=None):
        self.session=session
        if session is None:
            from altaircms.models import DBSession
            self.session = DBSession

    def fetch(self, name, pks):
        try:
            return getattr(self, name)(pks)
        except AttributeError as e:
            logging.exception(e)

            raise WidgetFetchException("self.%s() fetch method is not defined" % name)

    @classmethod
    def add_fetch_method(cls, name, widget):
        def _query(self, pks):
            return self._query_by_object(widget, pks)
        setattr(cls, name, _query)
        return cls

    def _query_by_object(self, model, pks):
        return self.session.query(model).filter(model.id.in_(pks))

