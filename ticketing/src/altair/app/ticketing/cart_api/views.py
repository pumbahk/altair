# -*- coding:utf-8 -*-
import logging

from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPNotFound

from altair.app.ticketing.cart.exceptions import OutTermSalesException

logger = logging.getLogger(__name__)


@view_defaults(renderer='json')
class CartAPIView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='cart.api.health_check')
    def health_check(self):
        return HTTPNotFound()

    @view_config(route_name='cart.api.index')
    def index(self):
        return dict(status='OK')

    @view_config(route_name='cart.api.performances')
    def performances(self):
        event = self.context.event
        return dict(
            performances=[dict(
                performance_id=p.id,
                performance_name=p.name,
                open_on=p.open_on,
                start_on=p.start_on,
                end_on=p.end_on,
                venue_id=p.venue.id,
                venue_name=p.venue.name,
                sales_segments=[dict(
                    sales_segment_id=ss.id,
                    sales_segment_name=ss.sales_segment_group.name
                ) for ss in p.sales_segments]
            ) for p in event.performances]
        )

    @view_config(route_name='cart.api.performance')
    def performance(self):
        performance = self.context.performance
        if performance is None:
            return HTTPNotFound()
        # available_sales_segments = performance.sales_segments  # TODO: fix to available ss only
        try:
            available_sales_segments = self.context.available_sales_segments
        except OutTermSalesException as e:
            # FIXME: handle error when no sales segment is available
            logger.error("no sales segment available now: {}".format(self.context.now))
            raise HTTPNotFound()
        return dict(
            performance=dict(
                performance_id=performance.id,
                performance_name=performance.name,
                open_on=performance.open_on,
                start_on=performance.start_on,
                end_on=performance.end_on,
                order_limit=performance.setting.order_limit,
                venue_id=performance.venue.id,
                venue_name=performance.venue.name
            ),
            event=dict(
                event_id=performance.event.id,
                order_limit=performance.event.setting.order_limit,
            ),
            sales_segments=[dict(
                sales_segment_id=ss.id,
                sales_segment_name=ss.sales_segment_group.name,
                start_at=ss.start_at,
                end_at=ss.end_at,
                seat_choice=ss.seat_choice,
                order_limit=ss.order_limit
            ) for ss in available_sales_segments]
        )

    @view_config(route_name='cart.api.stock_types')
    def stock_types(self):
        return {
            "stock_types": [{
                "stock_type_id": 12345,
                "stock_type_name": "バックネット裏指定席S",
                "is_quantity_only": False,
                "description": "注意事項など",
                "min_quantity": 1,
                "max_quantity": 20,
                "min_product_quantity": 1,
                "max_product_quantity": 20
            },
            {
                "stock_type_id": 12346,
                "stock_type_name": "内野指定席1塁側",
                "is_quantity_only": False,
                "description": "注意事項など",
                "min_quantity": 1,
                "max_quantity": 20,
                "min_product_quantity": 1,
                "max_product_quantity": 20
            },
            {
                "stock_type_id": 12347,
                "stock_type_name": "外野自由エリア",
                "is_quantity_only": True,
                "description": "注意事項など",
                "min_quantity": 1,
                "max_quantity": 20,
                "min_product_quantity": 1,
                "max_product_quantity": 20
            }]
        }

    @view_config(route_name='cart.api.stock_type')
    def stock_type(self):
        return {
            "stock_type": {
                "stock_type_id": 12345,
                "stock_type_name": "バックネット裏指定席S",
                "is_quantity_only": False,
                "description": "注意事項など",
                "min_quantity": 1,
                "max_quantity": 20,
                "min_product_quantity": 1,
                "max_product_quantity": 20,
                "products": [
                    {
                        "product_id": 10001,
                        "product_name": "大人",
                        "price": 5000,
                        "min_product_quantity": 1,
                        "max_product_quantity ": 20,
                        "is_must_be_chosen": True
                    },
                    {
                        "product_id": 10002,
                        "product_name": "子供",
                        "price": 2500,
                        "min_product_quantity": 1,
                        "max_product_quantity ": 20,
                        "is_must_be_chosen": False
                    }
                ],
                "blocks": ["b1", "b2", "b3"]
            }
        }

    @view_config(route_name='cart.api.seats')
    def seats(self):
        return {
            "stock_types": [
                {
                    "stock_type_id": 12345,
                    "available_counts": 3
                },
                {
                    "stock_type_id": 12346,
                    "available_counts": 2
                }
            ],
            "blocks": [
                {
                    "block_id": "A",
                    "available_counts": 3
                    },
                {
                    "block_id": "B",
                    "available_counts": 2
                    },
                {
                    "block_id": "C",
                    "available_counts": 0
                }
            ],
            "seats": [
                {
                    "seat_id": "A-01",
                    "is_available": False,
                    "stock_type_id": 12345
                },
                {
                    "seat_id": "A-02",
                    "is_available": False,
                    "stock_type_id": 12345
                },
                {
                    "seat_id": "A-03",
                    "is_available": False,
                    "stock_type_id": 12345
                },
                {
                    "seat_id": "A-04",
                    "is_available": False,
                    "stock_type_id": 12345
                },
                {
                    "seat_id": "A-05",
                    "is_available": True,
                    "stock_type_id": 12345
                }
            ]
        }



    @view_config(route_name='cart.api.seat_reserve')
    def seat_reserve(self):
        return {
            "results": {
                "status": "OK",
                "reserve_type": "seat_choise",
                "stock_type_id": 6789,
                "quantity": 2,
                "is_quantity_only": False,
                "is_separated": False,
                "seats": ["s01-r001-01", "s01-r001-02"]
            }
        }


    @view_config(route_name='cart.api.seat_release')
    def seat_release(self):
        return {
            "results": {
                "status": "OK",
                "stock_type_id": 6789,
                "quantity": 2,
                "is_quantity_only": False,
                "seats": ["s01-r001-01", "s01-r001-02"]
            }
        }

