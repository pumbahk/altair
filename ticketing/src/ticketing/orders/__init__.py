# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('orders.index'                     , '/')
    config.add_route('orders.show'                      , '/show/{order_id}')
    config.add_route('orders.cancel'                    , '/cancel/{order_id}')
    config.add_route('orders.delivered'                 , '/delivered/{order_id}')
    config.add_route('orders.download'                  , '/download/')

    config.add_route('orders.print.queue'               , '/print/queue/{order_id}')

    config.add_subscriber('.mail.on_order_canceled'     , '.events.OrderCanceled')

    config.add_route('orders.sej'                       , '/sej')
    config.add_route('orders.sej.event.refund'          , '/sej/event/refund')
    config.add_route('orders.sej.event.refund.add'      , '/sej/event/refund/add')
    config.add_route('orders.sej.event.refund.detail'   , '/sej/event/refund/{event_id}')

    config.add_route('orders.sej.order.request'         , '/sej/order/request')
    config.add_route('orders.sej.order.info'            , '/sej/order/{order_id}/')
    config.add_route('orders.sej.order.cancel'          , '/sej/order/{order_id}/cancel')
    config.add_route('orders.sej.order.ticket.data'     , '/sej/order/{order_id}/ticket/{ticket_id}/data')
    config.add_route('orders.sej.order.ticket.refund'   , '/sej/order/refund/{ticket_id}/ticket')

    config.add_route('orders.sej.ticket_template'       , '/sej/ticket_template')

    config.add_route("orders.api.performances"          , "/api/performances")
    config.scan(".")
