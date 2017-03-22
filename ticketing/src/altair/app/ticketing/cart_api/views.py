# -*- coding:utf-8 -*-
import logging

from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

from altair.sqlahelper import get_db_session
from altair.pyramid_dynamic_renderer import lbr_view_config

from altair.app.ticketing.core.models import StockType
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
        available_sales_segments = self.context.available_sales_segments
        available_ss_per_perfromance = {}
        for ss in available_sales_segments:
            if ss.performance not in available_ss_per_perfromance.keys():
                available_ss_per_perfromance[ss.performance] = [ss]
            else:
                available_ss_per_perfromance[ss.performance].append(ss)
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
                ) for ss in available_ss_per_perfromance[p]]
            ) for p in available_ss_per_perfromance.keys()]
        )

    @view_config(route_name='cart.api.performance')
    def performance(self):
        performance = self.context.performance
        if performance is None:
            raise HTTPNotFound('performance_id={} not found'.format(self.request.matchdict.get('performance_id')))

        available_sales_segments = self.context.available_sales_segments
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
        stock_types = self.context.performance.stock_types
        return dict(
            stock_types=[dict(
                stock_type_id=st.id,
                stock_type_name=st.name,
                is_quantity_only=st.quantity_only,
                description=st.description,
                min_quantity=st.min_quantity,
                max_quantity=st.max_quantity,
                min_product_quantity=st.min_product_quantity,
                max_product_quantity=st.max_product_quantity
            ) for st in stock_types]
        )

    @view_config(route_name='cart.api.stock_type')
    def stock_type(self):
        performance = self.context.performance
        stock_type_id = self.request.matchdict.get('stock_type_id')
        session = get_db_session(self.request, 'slave')
        try:
            stock_type = session.query(StockType).filter(StockType.id == stock_type_id).one()
        except NoResultFound as e:
            logger.warning("{} for stock_type_id={}".format(e.message, stock_type_id))
            raise HTTPNotFound()
        products = [p for p in stock_type.product if p.performance_id == performance.id]  # XXX: productだけどlistが返ってくる
        # TODO: blocksが何者か確認して修正する
        return dict(
            stock_type=dict(
                stock_type_id=stock_type.id,
                stock_type_name=stock_type.name,
                is_quantity_only=stock_type.quantity_only,
                description=stock_type.description,
                min_quantity=stock_type.min_quantity,
                max_quantity=stock_type.max_quantity,
                min_product_quantity=stock_type.min_product_quantity,
                max_product_quantity=stock_type.max_product_quantity,
                products=[dict(
                    product_id=product.id,
                    product_name=product.name,
                    price=product.price,
                    min_product_quantity=product.min_product_quantity,
                    max_product_quantity=product.max_product_quantity,
                    is_must_be_chosen=product.must_be_chosen
                ) for product in products],
                blocks=["dummy"]
            )
        )
        # return {
        #     "stock_type": {
        #         "stock_type_id": 12345,
        #         "stock_type_name": "バックネット裏指定席S",
        #         "is_quantity_only": False,
        #         "description": "注意事項など",
        #         "min_quantity": 1,
        #         "max_quantity": 20,
        #         "min_product_quantity": 1,
        #         "max_product_quantity": 20,
        #         "products": [
        #             {
        #                 "product_id": 10001,
        #                 "product_name": "大人",
        #                 "price": 5000,
        #                 "min_product_quantity": 1,
        #                 "max_product_quantity ": 20,
        #                 "is_must_be_chosen": True
        #             },
        #             {
        #                 "product_id": 10002,
        #                 "product_name": "子供",
        #                 "price": 2500,
        #                 "min_product_quantity": 1,
        #                 "max_product_quantity ": 20,
        #                 "is_must_be_chosen": False
        #             }
        #         ],
        #         "blocks": ["b1", "b2", "b3"]
        #     }
        # }

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


@view_config(context=OutTermSalesException, renderer='json')
def out_term_exec(context, request):
    request.response.status = 404
    message = context.message or 'no resource was found'
    return dict(
            error=dict(
                code="404",
                message="{}: {}".format(context.__class__.__name__, message),
                details=[]
            )
        )


@view_config(context=HTTPNotFound, renderer='json')
def no_resource(context, request):
    request.response.status = 404
    message = context.message or 'no resource was found'
    return dict(
        error=dict(
            code="404",
            message="{}: {}".format(context.__class__.__name__, message),
            details=[]
        )
    )
