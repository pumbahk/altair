# -*- coding: utf-8 -*-
from altair.app.ticketing.famiport.userside_models import AltairFamiPortPerformance, AltairFamiPortReflectionStatus
from altair.app.ticketing.payments import plugins

def get_famiport_reflect_button_status(session, event):
        altair_famiport_performances = session.query(AltairFamiPortPerformance) \
            .filter(AltairFamiPortPerformance.performance_id.in_([prfm.id for prfm in event.performances])) \
            .filter(AltairFamiPortPerformance.status == AltairFamiPortReflectionStatus.Reflected.value) \
            .all()

        def has_famiport_pdmp(sales_segment):
            for pdmp in sales_segment.payment_delivery_method_pairs:
                if pdmp.payment_method.payment_plugin_id == plugins.FAMIPORT_PAYMENT_PLUGIN_ID \
                        or pdmp.delivery_method.delivery_plugin_id == plugins.FAMIPORT_DELIVERY_PLUGIN_ID:
                    return True
            return False

        if not altair_famiport_performances:
            return u'NONE_REFLECTED'
        elif len(altair_famiport_performances) == len(event.performances):
            altair_famiport_sales_segments = []
            sales_segments = []
            for fmp in altair_famiport_performances:
                # 数受け、指定席によってプロパティが違うので両方みる
                unselectable_ss_ids = [ss.seat_unselectable_sales_segment_id for ss in fmp.altair_famiport_sales_segment_pairs if ss.seat_unselectable_sales_segment_id]
                selectable_ss_ids = [ss.seat_selectable_sales_segment_id for ss in fmp.altair_famiport_sales_segment_pairs if ss.seat_selectable_sales_segment_id]
                altair_famiport_sales_segments.extend(unselectable_ss_ids)
                altair_famiport_sales_segments.extend(selectable_ss_ids)
            for p in event.performances:
                for ss in p.sales_segments:
                    if has_famiport_pdmp(ss):
                        sales_segments.extend([ss.id])
            if set(altair_famiport_sales_segments) == set(sales_segments):
                return u'ALL_REFLECTED'
            else:
                return u'SOME_REFLECTED'
        else:
            return u'SOME_REFLECTED'