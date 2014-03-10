#-*- coding: utf-8 -*-
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap

class _GettiiBaseView(BaseView):
    pass

@view_defaults(route_name='gettii.venue', decorator=with_bootstrap, permission='event_editor')
class VenueView(_GettiiBaseView):

    @view_config(route_name='gettii.venue.index', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/gettii/venues.html')
    def index(self):
        return {'venue': self.context.venue,
                'external_venues': self.context.external_venues,
                'upload_form': ExternalVenueUploadForm(),
                }

    @view_config(route_name='gettii.venue.download', request_method='GET'):
    def download(self):
        return {'venue': self.context.venue,
                'external_venues': self.context.external_venues,
                'upload_form': ExternalVenueUploadForm(),
                }

    @view_config(route_name='gettii.venue.upload', request_method='GET'):
    def upload(self):
        return {'venue': self.context.venue,
                'external_venues': self.context.external_venues,
                'upload_form': ExternalVenueUploadForm(),
                }
