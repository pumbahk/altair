# -*- coding: utf-8 -*-
def includeme(config):
    config.add_route('orders.index'                     , '/')
    config.add_route('orders.checked.queue'             , '/checked/queue')
    config.add_route('orders.checked.delivered'         , '/checked/delivered')
    config.add_route('orders.show'                      , '/show/{order_id}', factory=".resources.OrdersShowResource")
    config.add_route('orders.edit.shipping_address'     , '/edit/{order_id}/shipping_address/')
    config.add_route('orders.edit.product'              , '/edit/{order_id}/product/')
    config.add_route('orders.cancel'                    , '/cancel/{order_id}')
    config.add_route('orders.delete'                    , '/delete/{order_id}')
    config.add_route('orders.delivered'                 , '/delivered/{order_id}')
    config.add_route('orders.undelivered'               , '/undelivered/{order_id}')
    config.add_route('orders.change_status'             , '/change_status/{order_id}/{status}')
    config.add_route('orders.download'                  , '/download/')
    config.add_route('orders.sales_summary'             , '/sales_summary/')
    config.add_route('orders.reserve.form'              , '/reserve/form/')
    config.add_route('orders.reserve.form.reload'       , '/reserve/form/reload/')
    config.add_route('orders.reserve.confirm'           , '/reserve/confirm/')
    config.add_route('orders.reserve.complete'          , '/reserve/complete/')
    config.add_route('orders.reserve.reselect'          , '/reserve/reselect/')
    config.add_route('orders.memo_on_order'             , '/memo_on_order/{order_id}')
    config.add_route('orders.attributes_edit'           , '/attributes/edit/{order_id}')
    config.add_route('orders.note'                      , '/note/{order_id}')
    config.add_route('orders.issue_status'              , '/issue_status/{order_id}')
    config.add_route('orders.api.get'                   , '/api/get/')

    config.add_route('orders.refund.index'              , '/refund/')
    config.add_route('orders.refund.search'             , '/refund/search/')
    config.add_route('orders.refund.checked'            , '/refund/checked/')
    config.add_route('orders.refund.confirm'            , '/refund/confirm/')
    config.add_route('orders.refund.immediate'          , '/refund/immediate/{order_id}')

    config.add_route('orders.fraud.clear'               , '/fraud/clear/{order_id}')

    config.add_route("orders.cover.preview"             , "/cover/preview/{order_id}/cover")
    config.add_route("orders.ticket.placeholder"        , "/api/preview/order/{order_id}/placeholders")
    config.add_route("orders.item.preview"              , "/item/preview/{order_id}/item/{item_id}", factory=".resources.OrderPreviewResource")
    config.add_route("orders.item.preview.getdata"      , "/api/item/{item_id}/ticket/{ticket_format_id}")
    config.add_route('orders.print.queue'               , '/print/queue/{order_id}')
    config.add_route('orders.print.queue.each'               , '/print/queue/each/{order_id}', factory=".resources.OrderPrintEachResource")
    config.add_route('orders.print.queue.dialog'        , '/api/print/queue/{order_id}')

    config.add_subscriber('.mail.on_order_canceled'     , '.events.OrderCanceled')

    config.add_route('orders.sej'                       , '/sej')
    config.add_route('orders.sej.event.refund'          , '/sej/event/refund')
    config.add_route('orders.sej.event.refund.add'      , '/sej/event/refund/add')
    config.add_route('orders.sej.event.refund.detail'   , '/sej/event/refund/{event_id}')

    config.add_route('orders.sej.order.request'         , '/sej/order/request')
    config.add_route('orders.sej.order.info'            , '/sej/order/{order_no}/')
    config.add_route('orders.sej.order.cancel'          , '/sej/order/{order_no}/cancel')
    config.add_route('orders.sej.order.ticket.data'     , '/sej/order/{order_no}/ticket/{ticket_id}/data')
    config.add_route('orders.sej.order.ticket.refund'   , '/sej/order/refund/{ticket_id}/ticket')

    config.add_route('orders.sej.ticket_template'       , '/sej/ticket_template')

    config.add_route("orders.mailinfo"                  , "/orders/{order_id}/mailinfo/{action}")
    config.add_route("orders.api.performances"          , "/api/performances")
    config.add_route("orders.api.sales_segment_groups"  , "/api/sales_segment_groups")
    config.add_route("orders.api.checkbox_status"       , "/api/checkbox_status/{action}")
    config.add_route("orders.api.orders"                , "/api/orders/{action}")
    config.add_route("cart.search",                       "/carts/")
    config.scan(".")

    # 団体予約、インナー予約でcartパッケージを使う為の設定
    from pyramid.interfaces import IRequest
    from altair.app.ticketing.cart.interfaces import IStocker, IReserving, ICartFactory
    from altair.app.ticketing.cart.stocker import Stocker
    from altair.app.ticketing.cart.reserving import Reserving
    from altair.app.ticketing.cart.carting import CartFactory
    reg = config.registry
    reg.adapters.register([IRequest], IStocker, "", Stocker)
    reg.adapters.register([IRequest], IReserving, "", Reserving)
    reg.adapters.register([IRequest], ICartFactory, "", CartFactory)

    ##metadata
    config.include("altair.metadata") #xxx:
    from altair.metadata import DefaultModelAttributeMetadataProviderRegistry
    from .metadata import METADATA_NAME_ORDERED_PRODUCT
    config.set_model_metadata_provider_registry(DefaultModelAttributeMetadataProviderRegistry(),
                                                name=METADATA_NAME_ORDERED_PRODUCT)
    from .metadata import METADATA_NAME_ORDER, order_metadata_provider
    order_attrs_registry = DefaultModelAttributeMetadataProviderRegistry()
    order_attrs_registry.registerProvider(order_metadata_provider)
    config.set_model_metadata_provider_registry(order_attrs_registry,
                                                name=METADATA_NAME_ORDER)



