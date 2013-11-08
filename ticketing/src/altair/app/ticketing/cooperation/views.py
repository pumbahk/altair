# -*- coding: utf-8 -*-
from pyramid.view import view_defaults, view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap

from .forms import CooperationUpdateForm, CooperationDownloadForm
GOOGLE = 'http://www.google.com'


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
        from mock import Mock
        site = Mock()
        site.name = u'テスト'
        update_form = CooperationUpdateForm()
        download_form = CooperationDownloadForm()
        return {'site': site,
                'update_form': update_form,
                'download_form': download_form,
                'display_modal': False,
                }

    @view_config(route_name='cooperation.download', request_method='GET')
    def download(self):
        res = Response()
        res.status = '200 OK'
        res.status_int = 200
        res.content_type = 'text/plain'
        res.charset = 'utf-8'
        res.headerlist = [
            ('Set-Cookie', 'abc=123'),
            ('X-My-Header', 'foo'),
            ]
        res.cache_for = 3600
        return res

    @view_config(route_name='cooperation.update', request_method='POST',
                 renderer='altair.app.ticketing:templates/cooperation/show.html')
    def update(self):
        form = CooperationUpdateForm(self.request.params)
        display_modal = False
        if form.validate() and hasattr(form.cooperation_file.data, 'file'):
            venue_id = form.venue_id.data
            organization_id = form.organization_id.data
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
        return {'site': site,
                'update_form': update_form,
                'download_form': download_form,
                'display_modal': display_modal,
                }


class VenueDoesNotExist(Exception):
    pass

class AugusVenueDoesNotExist(Exception):
    pass

class SeatDoesNotExist(Exception):
    pass

class InvalidStatus(Exception):
    pass

import csv
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from altair.app.ticketing.core.models import Venue, Seat, AugusVenue, AugusSeat

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
        area_code = int(row[7]) # H
        info_code = int(row[8]) # I
        seat_id = int(row[18]) # S
        
        augus_venue.code = augus_venue_code
        augus_venue.venue_id = venue.id
        augus_venue.save()
        seat = Seat.query.get(seat_id)
        if seat is None:
            raise SeatDoesNotExist()
            
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
        raise VenueDoesNotExist('Not found input venue: id={0}'.format(venue_id))
    qs = Venue.query.filter(Venue.site_id==venue.site_id,
                            Venue.performance_id==None,
                            )

    if not organization_id is None:
        qs = qs.filter(Venue.organization_id==organization_id)
    
    original_venue = qs.one() # raise sqlalchemy.orm.exc.NoResultFound or sqlalchemy.orm.exc.MultipleResultsFound
    
    if original_venue:
        return original_venue
    else:
        raise VenueDoesNotExist(
            'Not found original venue: input venue id={0})'.format(venue_id))
