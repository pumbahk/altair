# -*- coding: utf-8 -*-
import os
import csv
import json
from pyramid.view import view_defaults, view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, HTTPNotFound

from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import (
    Seat,
    Event,
    Performance,
    AugusPerformance,
    AugusVenue,
    GettiiVenue,
    )

from .utils import CSVEmptyError
from .forms import (
    CooperationUpdateForm,
    CooperationDownloadForm,
    CooperationTypeForm,
    )
from .augus2 import (
    CSVEditorFactory,
    ImporterFactory,
    NoSeatError,
    EntryFormatError,
    SeatImportError,
    )



@view_defaults(decorator=with_bootstrap, permission='event_editor')
class CooperationView(BaseView):
    def _stub(self):
        event_id = long(self.request.matchdict['event_id']) # raise KeyError, ValueError, TypeError
        event = Event.get(event_id)
        url = self.request.route_path('cooperation2.api.performances', event_id=event.id)
        if event:
            pairs = []
            for performance in event.performances:
                external_performance = AugusPerformance.get(performance.id)
                pairs.append((performance, external_performance))
            return {'event': event,
                    'performances': event.performances,
                    'save_url': url,
                    }
        else:
            raise HTTPNotFound('event_id: {0}'.format(event_id))

    @view_config(route_name='cooperation.get_seat_l0_ids', request_method='POST', renderer='json')
    def get_seat_l0_ids(self):
        performance_id = int(self.request.matchdict.get('performance_id'))
        performance = Performance.query.filter(Performance.id==performance_id).one()
        fmt_ = self.request.params.get('format')

        parent_venue = Venue.query.filter(Venue.site_id==performance.venue.site_id)\
                                  .filter(Venue.performance_id==None)\
                                  .one()
        if fmt_ == 'altair':
            success = {}
            fail = {}
            import csv
            seats = dict([(seat.l0_id, seat.l0_id) for seat in parent_venue.seats])
            reader = csv.reader(self.request.POST['csvfile'].file)
            try:
                reader.next() # headerを捨てる
            except (csv.Error, StopIteration) as err:
                raise HTTPBadRequest(body=json.dumps({
                    'message':u'ファイルが空です',
                }))

            try:
                for record in reader:
                    id = record[0]
                    gettii_venue_code = record[6]
                    l0_id = record[1].strip().decode('cp932')
                    name = record[3].strip().decode('cp932')
                    seat = seats.get(l0_id, None)
                    if seat and not (id is None) and id.isdigit() and not (gettii_venue_code is None) and gettii_venue_code.isdigit():
                        success[name] = l0_id
                    else:
                        fail[name] = l0_id
            except IndexError as err:
                raise HTTPBadRequest(body=json.dumps({
                    'message':u'ファイルフォーマットが不正です',
                }))

            return {'success': success,
                    'fail': fail,
                    }
        elif fmt_ == 'gettii':
            import datetime
            from .gettii.csvfile import GettiiSeatCSV
            external_seat_csv = GettiiSeatCSV()
            try:
                external_seat_csv.read_csv(self.request.POST['csvfile'].file)
            except CSVEmptyError as err:
                raise HTTPBadRequest(body=json.dumps({
                    'message':u'ファイルが空です',
                }))
            except AttributeError as err:
                raise HTTPBadRequest(body=json.dumps({
                    'message':u'ファイルが選択されていません',
                }))

            records = [record for record in external_seat_csv]

            # 公演日時でバリデーション
            try:
                record = None  # AltairGettiiVenueCSVRecordのインスタンスが入ります (recordsがなければNone)
                for record in records:
                    if record.venue_code:
                        start_on = datetime.datetime.strptime(record.start_day + ' ' + record.start_time, '%Y/%m/%d %H:%M')
                        if start_on != performance.start_on:
                            raise HTTPBadRequest(body=json.dumps({
                                'message': u'公演日時が一致しないものがありました',
                            }))
            except ValueError:
                raise HTTPBadRequest(body=json.dumps({
                    'message': u'不正なデータがありました: {}'.format(record),
                    }))

            external_venue_codes = list(set([row.venue_code for row in records]))
            if len(external_venue_codes) != 1:
                raise HTTPBadRequest(body=json.dumps({
                    'message':u'複数の会場コードは受け付けられません',
                }))

            external_venue_code = external_venue_codes[0]

            external_venue = None
            try:
                external_venue = GettiiVenue.query.filter(GettiiVenue.code==external_venue_code).one()
            except NoResultFound:
                raise HTTPBadRequest(body=json.dumps({
                    'message':u'指定された会場コードを持つGettii会場が見つかりませんでした',
                }))
            id_seat = dict([(ex_seat.l0_id, ex_seat) for ex_seat in external_venue.gettii_seats])

            success = {}
            fail = {}

            for record in records:
                ex_seat = id_seat.get(record.l0_id, None)
                if ex_seat:
                    success[record.l0_id] = ex_seat.seat.l0_id
                else:
                    fail[record.l0_id] = None
            return {'success': success,
                    'fail': fail,
                    }
        elif fmt_ == 'augus':
            raise HTTPBadRequest(body=json.dumps({
                'message':u'この機能はまだ使用できません',
            }))
        else:
            raise HTTPBadRequest(body=json.dumps({
                'message':u'この機能はまだ使用できません',
            }))

    # distribution
    @view_config(route_name='cooperation2.distribution', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/distribution.html')
    def distribution_get(self):
        return self._stub()

    @view_config(route_name='cooperation2.distribution', request_method='POST',
                 renderer='altair.app.ticketing:templates/cooperation/distribution.html')
    def distribution_post(self):
        return self._stub()

    # putback
    @view_config(route_name='cooperation2.putback', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/putback.html')
    def putback_get(self):

        return self._stub()

    @view_config(route_name='cooperation2.putback', request_method='POST',
                 renderer='altair.app.ticketing:templates/cooperation/putback.html')
    def putback_post(self):
        return self._stub()

    # achievement
    @view_config(route_name='cooperation2.achievement', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/achievement.html')
    def achievement_get(self):
        return self._stub()

    @view_config(route_name='cooperation2.achievement', request_method='POST',
                 renderer='altair.app.ticketing:templates/cooperation/achievement.html')
    def achievement_post(self):
        return self._stub()

    # events
    @view_config(route_name='cooperation2.events', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/events.html')
    def events_get(self):
        event_id = long(self.request.matchdict['event_id']) # raise KeyError, ValueError, TypeError
        event = Event.get(event_id)
        url = self.request.route_path('cooperation2.api.performances', event_id=event.id)
        if event:
            pairs = []
            for performance in event.performances:
                external_performance = AugusPerformance.get(performance.id)
                pairs.append((performance, external_performance))
            return {'event': event,
                    'performances': event.performances,
                    'save_url': url,
                    }
        else:
            raise HTTPNotFound('event_id: {0}'.format(event_id))

    @view_config(route_name='cooperation2.api.performances',
                 request_method='GET', renderer='json')
    def get_performances(self):
        event_id = self.request.matchdict['event_id'] # raise KeyError
        event_id = long(event_id) # raise TypeError or ValueError
        event = Event.get(event_id)
        entries = []
        if not event:
            raise HTTPNotFound('Not found event: event_id={0}'.format(repr(event_id)))
        for performance in event.performances:
            entry = {'id': performance.id,
                     'name': performance.name,
                     'code': performance.code,
                     'start_on': str(performance.start_on),
                     'venue': performance.venue.name,
                     'external_code': '',
                     'external_detail': '',
                     }
            external = AugusPerformance.get(performance_id=performance.id)
            if external:
                entry['external_code'] = external.code
                entry['external_detail'] = external.code
            entries.append(entry)
        return {'total': len(entries),
                'page': 1,
                'records': len(entries),
                'rows': entries,
                }

    @view_config(route_name='cooperation2.api.performances',
                 request_method='POST', renderer='json')
    def save_performances(self):
        success = {}
        illegal = {}

        for performance_id, external_performance_code in self.request.json.items():
            try:
                performance_id = long(performance_id)
            except (ValueError, TypeError) as err:
                illegal[performance_id] = external_performance_code

            performance = Performance.get(performance_id)
            if not performance:
                illegal[performance_id] = external_performance_code

            if external_performance_code:
                try:
                    external_performance_code = long(external_performance_code)
                except (ValueError, TypeError) as err:
                    illegal[performance_id] = external_performance_code
                external_performance = AugusPerformance.get(code=external_performance_code)
                if external_performance:
                    if external_performance.performance_id != performance.id:
                        external_performance.performance_id = performance.id;
                        external_performance.save()
                        success[performance_id] = external_performance_code
                else:
                    illegal[performance_id] = external_performance_code
            else: # delete link
                external_performance = AugusPerformance.get(performance_id=performance.id)
                if external_performance:
                    external_performance.performance_id = None
                    external_performance.save()
                else:
                    illegal[performance_id] = external_performance_code
        return {'illegal': illegal}


    # venues
    @view_config(route_name='cooperation2.show', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/show.html')
    def show(self):
        venue = self.context.venue
        update_form = CooperationUpdateForm()
        download_form = CooperationDownloadForm()
        cooperation_type_form = CooperationTypeForm()
        return {'venue': venue,
                'update_form': update_form,
                'download_form': download_form,
                'display_modal': False,
                'upload_url': self._upload_url(venue.id),
                'download_url': self._download_url(venue.id),
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

    @view_config(route_name='cooperation2.download', request_method='GET')
    def download(self):
        res = Response()
        writer = csv.writer(res, delimiter=',')
        csveditor = CSVEditorFactory.create(self.context.cooperation_type)
        try:
            csveditor.write(writer, self.context.pairs)
        except (NoSeatError, EntryFormatError, SeatImportError) as err:
            raise HTTPBadRequest(err)
        headers = self._create_res_headers(filename=csveditor.name)
        res.headers = headers
        return res

    @view_config(route_name='cooperation2.upload', request_method='POST')
    def upload(self):
        return_url = self.request.route_path('cooperation2.show',
                                             venue_id=self.context.venue.id)
        form = CooperationUpdateForm(self.request.params)
        if form.validate() and hasattr(form.cooperation_file.data, 'file'):
            reader = csv.reader(form.cooperation_file.data.file)
            importer = ImporterFactory.create(self.context.cooperation_type)
            try:
                importer.import_(reader, self.context.pairs)
            except (NoSeatError, EntryFormatError, SeatImportError) as err:
                raise HTTPBadRequest(err)
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
        raise HTTPFound(self.request.route_path('cooperation2.upload', venue_id=venue_id))

        #return {'site': site,
        #        'update_form': update_form,
        #        'download_form': download_form,
        #        'display_modal': display_modal,
        #        'upload_url': self._upload_url(venue_id)
        #        }

    def _upload_url(self, venue_id):
        return self.request.route_path('cooperation2.upload', venue_id=venue_id)

    def _download_url(self, venue_id):
        return self.request.route_path('cooperation2.download', venue_id=venue_id)

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
