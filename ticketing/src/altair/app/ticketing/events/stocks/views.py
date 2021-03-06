# -*- coding: utf-8 -*-

import json
import logging
import webhelpers.paginate as paginate
from datetime import datetime

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from pyramid.renderers import render_to_response
from pyramid.url import route_path
from sqlalchemy.sql import func
from wtforms import ValidationError
from paste.util.multidict import MultiDict

from altair.sqlahelper import get_db_session
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.lots.models import LotEntry, LotElectedEntry
from altair.app.ticketing.core.models import Stock, StockType, Seat, SeatStatusEnum, Venue, Performance
from altair.app.ticketing.events.stocks.forms import AllocateSeatForm, AllocateStockForm, AllocateStockTypeForm

logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class Stocks(BaseView):

    @view_config(route_name='stocks.allocate', request_method='POST', renderer='json')
    def allocate(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id, self.context.user.organization_id)
        if performance is None:
            logger.error('performance id %d is not found' % performance_id)
            raise HTTPBadRequest(body=json.dumps({
                'message':u'パフォーマンスが存在しません',
            }))

        # TKT-5590 在庫ロックのない当選中は、配席できないようにする
        lot_ids = [lot.id for lot in performance.event.lots]
        session = get_db_session(self.request, 'slave')
        electing = session.query(LotElectedEntry).join(LotEntry,
                                                       LotEntry.id == LotElectedEntry.lot_entry_id).filter(
            LotElectedEntry.completed_at == None).filter(LotEntry.lot_id.in_(lot_ids)).first()
        if electing:
            raise HTTPBadRequest(body=json.dumps({
                'message': u'大規模当選処理(テスト版)を使用しています。在庫数確定がされていない抽選があります',
            }))

        post_data = MultiDict(self.request.json_body)
        if not post_data.get('seats') and not post_data.get('stocks') and not post_data.get('stock_types'):
            raise HTTPBadRequest(body=json.dumps({
                'message':u'保存対象がありません',
            }))

        try:
            for post_seat in post_data.get('seats'):
                f = AllocateSeatForm(MultiDict(post_seat), stocks=post_data.get('stocks'))
                if not f.validate():
                    raise ValidationError(reduce(lambda a,b: a+b, f.errors.values(),[]))

                seat = Seat.filter_by(l0_id=post_seat.get('id'))\
                           .join(Seat.venue)\
                           .filter(Venue.performance_id==performance_id).first()
                if seat and seat.status not in [SeatStatusEnum.NotOnSale.v, SeatStatusEnum.Vacant.v]:
                    raise ValidationError(u'配席を変更可能な座席ではありません (%s)' % seat.name)

                seat.stock_id = post_seat.get('stock_id')
                seat.save()

            now = datetime.now()
            for post_stock in post_data.get('stocks'):
                f = AllocateStockForm(MultiDict(post_stock))
                if not f.validate():
                    raise ValidationError(reduce(lambda a,b: a+b, f.errors.values(),[]))

                stock = Stock.filter_by(id=post_stock.get('id')).first()
                stock.quantity = f.quantity.data
                stock.locked_at = None if f.assignable.data else now
                stock.save()

            for post_stock_type in post_data.get('stock_types'):
                f = AllocateStockTypeForm(MultiDict(post_stock_type))
                if not f.validate():
                    raise ValidationError(reduce(lambda a,b: a+b, f.errors.values(),[]))

                stock_type = StockType.get(id=post_stock_type.get('id'))
                stock_type.name = post_stock_type.get('name')
                stock_type.style = post_stock_type.get('style')
                stock_type.save()

        except ValidationError, e:
            raise HTTPBadRequest(body=json.dumps({
                'message':e.message,
            }))

        except Exception, e:
            logger.exception('save error (%s)' % e.message)
            raise HTTPBadRequest(body=json.dumps({
                'message':u'例外が発生しました',
            }))

        return {'message':u'席種・配券先を保存しました'}
