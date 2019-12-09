# encoding: utf-8

from datetime import datetime
from marshmallow import Schema, fields, validates_schema, ValidationError, pre_dump

from altair.app.ticketing.core.models import Performance
from ..models import ResaleSegment, ResaleRequest


class ResaleSegmentSerializer(Schema):
    __model__ = ResaleSegment
    id = fields.Integer(load_from='resale_segment_id')
    performance_id = fields.Integer()
    reception_start_at = fields.DateTime('%Y-%m-%d %H:%M:%S',
                                         required=True,
                                         error_messages={
                                             'required': u"申込開始日時は必須項目です。",
                                             'invalid': u"申込開始日時を正しい日時に設定ください。"})
    reception_end_at = fields.DateTime('%Y-%m-%d %H:%M:%S',
                                       required=True,
                                       error_messages={
                                           'required': u"申込終了日時は必須項目です。",
                                           'invalid': u"申込終了日時を正しい日時に設定ください。"})
    resale_start_at = fields.DateTime('%Y-%m-%d %H:%M:%S',
                                      required=False,
                                      error_messages={'invalid': u"リセール開始日時を正しい日時に設定ください。"},
                                      missing=None)
    resale_end_at = fields.DateTime('%Y-%m-%d %H:%M:%S',
                                    required=False,
                                    error_messages={'invalid': u"リセール終了日時を正しい日時に設定ください。"},
                                    missing=None)
    sent_status = fields.Integer(required=False)
    sent_at = fields.DateTime('%Y-%m-%d %H:%M:%S',
                              required=False,
                              error_messages={'invalid': u"連携日時を正しい日時に設定ください。"})
    resale_performance_id = fields.Integer(required=False)

    @validates_schema
    def validate_start_and_end_at(self, data):
        _reception_start_at = data.get('reception_start_at')
        _reception_end_at = data.get('reception_end_at')
        _resale_start_at = data.get('resale_start_at')
        _resale_end_at = data.get('resale_end_at')
        _performance_id = data.get('performance_id')

        if _reception_start_at >= _reception_end_at:
            raise ValidationError(u'申込開始日時を申込終了日時より前に設定してください。', ['reception_start_at'])

        if _resale_start_at is not None and _resale_end_at is not None:
            if _resale_end_at <= _resale_start_at:
                raise ValidationError(u'リセール開始日時をリセール終了日より前に設定してください。', ['resale_start_at'])
            # 申込期間とリセール期間を並行稼働可能にする 
            # if _resale_start_at < _reception_end_at:
            #     raise ValidationError(u'リセール開始日時は申込終了日時より後に設定してください。', ['resale_start_at'])
        else:
            if not (_resale_start_at is None and _resale_end_at is None):
                raise ValidationError(u'リセール開始日時とリセール終了日時は両方とも入力してください。', ['resale_start_at'])

        try:
            _performance = Performance.query.filter_by(id=_performance_id).one()
        except:
            raise ValidationError(u'リセール元の公演（ID: {}）は見つかりませんでした。'.format(_performance_id))

        if _resale_end_at:
            if _performance.open_on:
                if _performance.open_on.replace(hour=0, minute=0, second=0, microsecond=0) <= _resale_end_at:
                    raise ValidationError(u'リセール終了日時は公演日の１日前までに設定してください。', ['resale_end_at'])
            else:
                if _performance.start_on.replace(hour=0, minute=0, second=0, microsecond=0) <= _resale_end_at:
                    raise ValidationError(u'リセール終了日時は公演日の１日前までに設定してください。', ['resale_end_at'])

        _sales_segments = _performance.sales_segments

        _start_on = None
        for _sales_segment in _sales_segments:
            _sales_segment_group = _sales_segment.sales_segment_group
            if _sales_segment_group.kind == u'normal':
                if _start_on is None:
                    _start_on = _sales_segment.start_at
                    continue

                if _sales_segment.start_at < _start_on:
                    _start_on = _sales_segment.start_at

        if _start_on:
            if _reception_start_at < _start_on:
                raise ValidationError(u'申込開始日時を販売開始日時の後にしてください', ['reception_start_at'])

    @validates_schema
    def validate_resale_performance_id_exist(self, data):

        resale_segment_id = data.get('id')
        performance_id = data.get('performance_id')
        resale_performance_id = data.get('resale_performance_id')

        if resale_performance_id:
            if ResaleSegment.query \
                    .filter(ResaleSegment.id != resale_segment_id) \
                    .filter_by(resale_performance_id=resale_performance_id).count() > 0:
                raise ValidationError(
                    u'登録したいリセール公演の公演はすでに他のリセール区分に登録されています。',
                    ['resale_performance_id'])

            try:
                p = Performance.query.filter_by(id=performance_id).one()
            except:
                raise ValidationError(
                    u'リセール元の公演（ID: {}）は見つかりませんでした。'.format(performance_id))
            try:
                p_resale = Performance.query.filter_by(id=resale_performance_id).one()
            except:
                raise ValidationError(
                    u'登録したいリセール公演の公演（ID: {}）は存在していません。'.format(resale_performance_id),
                    ['resale_performance_id'])

            if p.event.organization.id != p_resale.event.organization.id:
                raise ValidationError(
                    u'登録したいリセール公演の公演は{}の公演のみ登録できます。'.format(
                        p.event.organization.name),
                    ['resale_performance_id'])

            if p_resale.start_on < datetime.now() or (p_resale.end_on and p_resale.end_on < datetime.now()):
                raise ValidationError(
                    u'登録したいリセール公演の公演はすでに終了しています。', ['resale_performance_id'])


class ResaleSegmentCreateSerializer(ResaleSegmentSerializer):
    performance_id = fields.Integer(required=True)


class ResaleRequestSerializer(Schema):
    __model__ = ResaleRequest
    id = fields.Integer()
    resale_segment_id = fields.Integer(required=True)
    ordered_product_item_token_id = fields.Integer(required=True)
    bank_code = fields.String(required=True)
    bank_branch_code = fields.String(required=True)
    account_type = fields.String(required=True)
    account_number = fields.String(required=True)
    account_holder_name = fields.String(required=True)
    total_amount = fields.Number(required=True)


class ResaleRequestExportAPISerializer(ResaleRequestSerializer):
    order_no = fields.String(required=True)
    performance_name = fields.String(required=True)
    performance_start_on = fields.DateTime('%Y-%m-%d %H:%M:%S', required=False, missing=None)

    @pre_dump(pass_many=True)
    def horizontal(self, data, many, **kwargs):
        for index, record in enumerate(data):
            resale_request = record.ResaleRequest
            resale_request.order_no = record.order_no
            resale_request.performance_name = record.performance_name
            resale_request.performance_start_on = record.performance_start_on
            data[index] = resale_request
        return data


class ResaleRequestVenueExportAPISerializer(Schema):
    seat_name = fields.String(required=True)
    performance_name = fields.String(required=True)
    performance_start_on = fields.DateTime('%Y-%m-%d %H:%M:%S', required=True)
    venue_name = fields.String(required=True)
    product_item_name = fields.String(required=True)

    @pre_dump(pass_many=True)
    def horizontal(self, data, many, **kwargs):
        for index, record in enumerate(data):
            resale_request = record.ResaleRequest
            resale_request.seat_name = record.seat_name
            resale_request.performance_name = record.performance_name
            resale_request.performance_start_on = record.performance_start_on
            resale_request.venue_name = record.venue_name
            resale_request.product_item_name = record.product_item_name
            data[index] = resale_request
        return data
