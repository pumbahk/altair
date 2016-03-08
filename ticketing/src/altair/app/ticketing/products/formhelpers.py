# -*- coding: utf-8 -*-
from wtforms.validators import ValidationError
from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID


def validate_ticket_bundle_and_sales_segment_set(ticket_bundle, sales_segment):
    plugin_ids_in_bundle = set()
    # 紐付けられた券面構成のplugin_idsを取得
    for ticket in ticket_bundle.tickets:
        plugin_ids_in_bundle.update([method.delivery_plugin_id for method in ticket.ticket_format.delivery_methods])

    for pdmp in sales_segment.payment_delivery_method_pairs:
        deli_plugin_id = pdmp.delivery_method.delivery_plugin_id
        if deli_plugin_id == SEJ_DELIVERY_PLUGIN_ID:
            if SEJ_DELIVERY_PLUGIN_ID not in plugin_ids_in_bundle:
                raise ValidationError(u'券面構成に必要なsej券面が紐付いていません')
        elif deli_plugin_id == FAMIPORT_DELIVERY_PLUGIN_ID:
            if FAMIPORT_DELIVERY_PLUGIN_ID not in plugin_ids_in_bundle:
                raise ValidationError(u'券面構成に必要なfamiport券面が紐付いていません')
