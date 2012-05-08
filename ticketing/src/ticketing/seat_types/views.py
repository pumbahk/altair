 # -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.products.models import SeatType
from ticketing.seat_types.forms import SeatTypeForm

import sqlahelper
session = sqlahelper.get_session()

@view_defaults(decorator=with_bootstrap)
class SeatTypes(BaseView):

    @view_config(route_name='seat_types.new', request_method='POST')
    def new_post(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))

        f = SeatTypeForm(self.request.POST)
        data = f.data
        style = {
            'stroke' : {
                'color'     : data.get('stroke_color'),
                'width'     : data.get('stroke_width'),
                'pattern'   : data.get('stroke_patten'),
            },
            'fill': {
                'color'     : data.get('fill_color'),
                'type'      : data.get('fill_type'),
                'image'     : data.get('fill_image'),
            },
            'text'          : data.get('text'),
            'text_color'    : data.get('text_color'),
        }
        record = merge_session_with_post(SeatType(), data)
        record.style = style

        record.performance_id = performance_id
        SeatType.add(record)

        self.request.session.flash(u'席種を保存しました')
        return HTTPFound(location=route_path('performances.show', self.request, performance_id=performance_id))

    @view_config(route_name='seat_types.edit', request_method='POST')
    def edit_post(self):
        seat_type_id = int(self.request.matchdict.get('seat_type_id', 0))
        seat_type = SeatType.get(seat_type_id)
        if seat_type is None:
            return HTTPNotFound('seat_type id %d is not found' % id)

        f = SeatTypeForm(self.request.POST)
        data = f.data
        style = {
            'stroke' : {
                'color'     : data.get('stroke_color'),
                'width'     : data.get('stroke_width'),
                'pattern'   : data.get('stroke_patten'),
            },
            'fill': {
                'color'     : data.get('fill_color'),
                'type'      : data.get('fill_type'),
                'image'     : data.get('fill_image'),
            },
            'text'          : data.get('text'),
            'text_color'    : data.get('text_color'),
        }
        seat_type.name          = data.get('name')
        seat_type.style         = style
        SeatType.update(seat_type)

        self.request.session.flash(u'席種を保存しました')
        return HTTPFound(location=route_path('performances.show', self.request, performance_id=seat_type.performance_id))

    @view_config(route_name='seat_types.delete')
    def delete(self):
        seat_type_id = int(self.request.matchdict.get('seat_type_id', 0))
        seat_type = SeatType.get(seat_type_id)
        if seat_type is None:
            return HTTPNotFound('seat_type id %d is not found' % id)

        SeatType.delete(seat_type)

        self.request.session.flash(u'席種を削除しました')
        return HTTPFound(location=route_path('performances.show', self.request, performance_id=seat_type.performance_id))

