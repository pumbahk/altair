# -*- coding: utf-8 -*-
import csv
from pyramid.view import view_defaults, view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound

from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import Seat
from .forms import (
    CooperationUpdateForm,
    CooperationDownloadForm,
    CooperationTypeForm,
    )
from .augus import (
    CSVEditorFactory,
    ImporterFactory,
    )

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class CooperationView(BaseView):

    @view_config(route_name='cooperation.index', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/index.html')
    def index(self):
        sitename_venueid = (('google', 'http://www.goolge.com'),)
        return {'sitename_venueid': sitename_venueid}

    @view_config(route_name='cooperation.show', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/show.html')
    def show(self):
        venue_id = int(self.request.matchdict.get('venue_id', 0))        
        from mock import Mock
        site = Mock()
        site.name = u'テスト'
        update_form = CooperationUpdateForm()
        download_form = CooperationDownloadForm()
        cooperation_type_form = CooperationTypeForm()
        return {'site': site,
                'update_form': update_form,
                'download_form': download_form,
                'display_modal': False,
                'upload_url': self._upload_url(venue_id),
                'download_url': self._download_url(venue_id),
                'cooperation_type_form': cooperation_type_form,
                }

    @staticmethod
    def _create_file_download_response_header(filename, timestamp=False, fmt='-%Y%m%d%H%M%S'):
        import time
        if timestamp:
            stamp = time.strftime(fmt) # raise TypeError
            name, ext = os.path.splitext(filename)
            filename = name + time.strftime(fmt) + ext

    @staticmethod
    def _create_res_headers(filename=None):
        return [('Content-Type', 'application/octet-stream; charset=cp932'),
                ('Content-Disposition', 'attachment; filename={0}'.format(filename)),
                ]

    @view_config(route_name='cooperation.download', request_method='GET')
    def download(self):
        res = Response()
        writer = csv.writer(res, delimiter=',')        
        csveditor = CSVEditorFactory.create(self.context.cooperation_type)
        csveditor.write(writer, self.context.pairs)
        headers = self._create_res_headers(filename=csveditor.name)
        res.headers = headers
        return res
        
    @view_config(route_name='cooperation.upload', request_method='POST')
    def upload(self):
        return_url = self.request.route_path('cooperation.show',
                                             venue_id=self.context.venue.id)
        form = CooperationUpdateForm(self.request.params)
        if form.validate() and hasattr(form.cooperation_file.data, 'file'):
            reader = csv.reader(form.cooperation_file.data.file)
            importer = ImporterFactory.create(self.context.cooperation_type)
            try:
                importer.import_(reader, self.context.pairs)
            except:
                raise
            else:
                return HTTPFound(return_url)
        else:# validate error
            raise HTTPFound(return_url)
                
    
    def _upload(self):
        venue_id = int(self.request.matchdict.get('venue_id', 0))
        organization_id = self.context.organization.id
        form = CooperationUpdateForm(self.request.params)
        display_modal = False
        if form.validate() and hasattr(form.cooperation_file.data, 'file'):
            cooperation_type = form.cooperation_type.data
            csv_file = form.cooperation_file.data.file
            update_augus_cooperation(venue_id, organization_id, csv_file)
        else:
            display_modal = True

        from mock import Mock
        site = Mock()
        site.name = u'テスト'
        update_form = form
        download_form = CooperationDownloadForm()
        raise HTTPFound(self.request.route_path('cooperation.upload', venue_id=venue_id))
        
        #return {'site': site,
        #        'update_form': update_form,
        #        'download_form': download_form,
        #        'display_modal': display_modal,
        #        'upload_url': self._upload_url(venue_id)
        #        }

    def _upload_url(self, venue_id):
        return self.request.route_path('cooperation.upload', venue_id=venue_id)

    def _download_url(self, venue_id):
        return self.request.route_path('cooperation.download', venue_id=venue_id)
        
class DeterminateError(Exception):
    pass

class NotFound(DeterminateError):
    pass

class MultipleFound(DeterminateError):
    pass

class DoesNotExist(Exception):
    pass

class VenueDoesNotExist(Exception):

    def __init__(self, venue_id, organization_id, msg=None):
        self.venue_id = venue_id
        self.organization_id = organization_id
        self.msg = msg

    def __str__(self):
        msg = 'Not found a venue: ' \
              'venue_id={0}, organization_id={1}'.format(
                  self.venue_id, self.organization_id)
        if self.msg:
            msg += '({0})'.format(self.msg)
        return msg
        

class AugusVenueDoesNotExist(Exception):
    pass

class SeatDoesNotExist(Exception):
    pass

class InvalidStatus(Exception):
    pass

import csv
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from altair.app.ticketing.core.models import Venue, Seat, AugusVenue, AugusSeat

def get_or_create_augus_venue(venue_id, code):
    try:
        return AugusVenue.query.filter(AugusVenue.venue_id==venue_id,
                                       AugusVenue.code==code).one()
    except NoResultFound as err:
        augus_venue = AugusVenue()
        augus_venue.venue_id = venue_id
        augus_venue.code = code
        augus_venue.save()
        return get_or_create_augus_venue(venue_id, code)
    except MultipleResultsFound as err:
        raise

def update_augus_cooperation(venue_id, organization_id, csvfile):
    venue = get_original_venue(venue_id, organization_id)
    try:
        augus_venue = AugusVenue.query.filter(AugusVenue.venue_id==venue_id).one()
    except NoResultFound as err:
        augus_venue = AugusVenue()
    except MultipleResultsFound as err:
        raise
        
    if not augus_venue:
        augus_venue = AugusVenue()
    
    augus_seats = AugusSeat.query.filter(
        AugusSeat.augus_venue_id==augus_venue.id)
    
    reader = csv.reader(csvfile)
    header = reader.next()
    for row in reader:
        augus_venue_code = unicode(row[0]) # A
        floor = unicode(row[6]) # G
        column = unicode(row[7]) # H
        num = unicode(row[8]) # I
        area_code = int(row[14]) # O
        info_code = int(row[15]) # P
        seat_id = int(row[18]) # S

        augus_venue = get_or_create_augus_venue(venue.id, augus_venue_code)
        seat = Seat.query.get(seat_id)
        if seat is None:
            raise SeatDoesNotExist()
        
        augus_seat = None
        try:
            augus_seat = augus_seats.filter(
                AugusSeat.augus_venue_id==augus_venue.id,
                AugusSeat.floor==floor,
                AugusSeat.column==column,
                AugusSeat.num==num,
                ).one()
        except NoResultFound as err:
            augus_seat = AugusSeat()
            augus_seat.augus_venue_id = augus_venue.id
            augus_seat.floor = floor
            augus_seat.column = column
            augus_seat.num = num
            augus_seat.area_code = area_code
            augus_seat.info_code = info_code
        except MultipleResultsFound as err:
            raise
        else:
            # check augus seat's validation.
            if augus_seat.augus_venue_id != augus_venue.id:
                raise InvalidStatus()
            if augus_seat.floor != floor:
                raise InvalidStatus()
            if augus_seat.column != column:
                raise InvalidStatus()
            if augus_seat.num != num:
                raise InvalidStatus()
            if augus_seat.area_code != area_code:
                raise InvalidStatus()                
            if augus_seat.info_code != info_code:
                raise InvalidStatus()                
        augus_seat.seat_id = seat.id
        augus_seat.save()



    
def get_original_venue(venue_id, organization_id=None):
    venue = Venue.query.get(venue_id)
    if not venue:
        raise VenueDoesNotExist(venue_id, organization_id)

    qs = Venue.query.filter(Venue.site_id==venue.site_id,
                            Venue.performance_id==None,
                            )

    if not organization_id is None:
        qs = qs.filter(Venue.organization_id==organization_id)

    try:
        original_venue = qs.one() # raise sqlalchemy.orm.exc.NoResultFound or sqlalchemy.orm.exc.MultipleResultsFound
    except NoResultFound as err:
        raise NotFound('Venue does not found: venue_id={0} organization_id={0}'.format(
            venue_id, organization_id))
    except MultipleResultsFound as err:
        raise MultipleFound('Venue does multiple found: venue_id={0} organization_id={0}'.format(
            venue_id, organization_id))
    
    if original_venue:
        return original_venue
    else:
        raise VenueDoesNotExist(venue_id, organization_id, 'original venue')        
