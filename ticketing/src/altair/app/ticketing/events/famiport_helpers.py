# -*- coding: utf-8 -*-
from sqlalchemy.orm.exc import NoResultFound
from altair.app.ticketing.famiport.exc import FamiPortAPINotFoundError
from altair.app.ticketing.famiport.userside_models import AltairFamiPortPerformance, AltairFamiPortReflectionStatus
from altair.app.ticketing.payments import plugins
from altair.app.ticketing.famiport import userside_api as fm_userside_api
from altair.app.ticketing.famiport import api as fm_api


def has_famiport_pdmp(sales_segment):
            for pdmp in sales_segment.payment_delivery_method_pairs:
                if pdmp.payment_method.payment_plugin_id == plugins.FAMIPORT_PAYMENT_PLUGIN_ID \
                        or pdmp.delivery_method.delivery_plugin_id == plugins.FAMIPORT_DELIVERY_PLUGIN_ID:
                    return True
            return False

def get_famiport_reflect_button_status(session, event):
        altair_famiport_performances = session.query(AltairFamiPortPerformance) \
            .filter(AltairFamiPortPerformance.performance_id.in_([prfm.id for prfm in event.performances])) \
            .filter(AltairFamiPortPerformance.status == AltairFamiPortReflectionStatus.Reflected.value) \
            .all()

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


def get_famiport_performance_ids(session, performances):
    # ファミポート連携されている公演IDを取得
    fm_performance_ids = []
    altair_famiport_performances = session.query(AltairFamiPortPerformance)\
        .filter(AltairFamiPortPerformance.performance_id.in_([performance.id for performance in performances])).all()
    for altair_famiport_performance in altair_famiport_performances:
        fm_performance_ids.append(altair_famiport_performance.performance_id)
    return fm_performance_ids

def needs_famiport_reflection(event):
    for ssg in event.sales_segment_groups:
        if has_famiport_pdmp(ssg):
            return True
    return False

# 連携が不足している項目を列挙
def get_famiport_reflection_warnings(request, session, performance):
    retval = {}
    warnings = set()
    altair_famiport_performance = fm_userside_api.get_altair_famiport_performance_by_performance(session, performance)
    # 未連携
    if not altair_famiport_performance:
        warnings.add(u'公演未連携')
    else:
        # 連携不足
        # 連携されるべき販売区分が不足していないかチェック
        ss_need_reflection = [ss for ss in performance.sales_segments if has_famiport_pdmp(ss)]
        altair_famiport_sales_segment_pairs = altair_famiport_performance.altair_famiport_sales_segment_pairs
        if len(ss_need_reflection) != len(altair_famiport_sales_segment_pairs):
            warnings.add(u'販売区分一部未連携')

        # 公演日が変更されていないかチェック
        if performance.start_on != altair_famiport_performance.start_at:
            warnings.add(u'公演日相違')

        # 会場が変更されていないかチェック
        altair_famiport_venue = altair_famiport_performance.altair_famiport_performance_group.altair_famiport_venue
        if performance.venue.site.siteprofile_id != altair_famiport_venue.siteprofile_id or \
            performance.venue.name != altair_famiport_venue.name:
            warnings.add(u'会場相違')

        # 販売区分チェック
        from altair.app.ticketing.core.models import FamiPortTenant
        tenant = session.query(FamiPortTenant)\
            .filter(FamiPortTenant.organization_id==performance.event.organization_id)\
            .one()
        for ss in altair_famiport_sales_segment_pairs:
            try:
                fmss_dict = fm_api.get_famiport_sales_segment_by_userside_id(request, tenant.code, ss.id)
            except FamiPortAPINotFoundError:
                continue
            origin_ss = ss.seat_unselectable_sales_segment or ss.seat_selectable_sales_segment
            # 開始日が変更されていないかチェック
            if ss.start_at != fmss_dict.get('start_at'):
                warnings.add(u'販売開始日相違')
            if ss.end_at != fmss_dict.get('end_at'):
                warnings.add(u'販売終了日相違')
            if origin_ss.name != fmss_dict.get('name'):
                warnings.add(u'販売区分名相違')

    retval[performance.id] = list(warnings)
    return retval

