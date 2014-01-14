# -*- coding: utf-8 -*-
import logging
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )

from altair.app.ticketing.views import BaseView as _BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from .forms import (
    PutbackForm,
    )
from altair.app.ticketing.core.models import (
    Stock,
    AugusPerformance,
    AugusSeat,
    AugusStockInfo,
    AugusPutback,
    )

logger = logging.getLogger(__name__)

class _CooperationView(_BaseView):
    pass

@view_defaults(route_name='cooperation.index', decorator=with_bootstrap, permission="event_editor")
class CooperationIndexView(_CooperationView):
    @view_config(request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/index.html')
    def index(self):
        return dict(event=self.context.event)

@view_defaults(route_name='cooperation.putback', decorator=with_bootstrap, permission="event_editor")
class CooperationPutbackView(_CooperationView):
    
    @view_config(request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/putback.html')
    def get(self):
        form = PutbackForm(event=self.context.event)
        params = dict(event=self.context.event,
                      form=form,
                      )
        return params
        
    @view_config(request_method='POST')
    def post(self):
        try:
            stock_holder_id = int(self.request.params.get('stock_holder_id'))
            performance_ids = map(int, self.request.params.getall('performance_ids'))
        except (TypeError, ValueError) as err:
            raise ValueError()
        
        stock_holder = None
        for stock_holder in self.context.event.stock_holders:
            if stock_holder.id == intstock_holder_id:
                break
        else:
            raise ValueError()
            
        performances = filter(lambda performance: performance.id in performance_ids,
                              self.context.event.performances)
        if not performances:
            raise ValueError()

        for performance in performances:
            unallcation_stock = Stock.query.filter(Stock.performance_id==performance.id)\
                                           .filter(Stock.stock_holder_id==None)\
                                           .filter(Stock.stock_type_id==None)\
                                           .one() # raise NoResultFound
            for stock in performance.stocks:
                for seat in Seat.query.filter(Seat.stock_id==stock.id):
                    ag_stock_info = AugusStockInfo.query.filter(AugusStockInfo.seat_id==seat.id).one()
                    ag_putback = AugusPutback()
                    ag_putback.augus_putback_code = u'test'
                    ag_putback.quantity = 1
                    ag_putback.augus_stock_info_id = ag_stock_info.id
                    ag_putback.seat_id = seat.id
                    ag_putback.reserved_at = datetime.now()
                    ag_putback.save()
        res = Response()
        return res
