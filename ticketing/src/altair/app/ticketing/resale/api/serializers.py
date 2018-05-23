# encoding: utf-8

from marshmallow import Schema, fields, validates_schema, ValidationError
from ..models import ResaleSegment, ResaleRequest

class ResaleSegmentSerializer(Schema):
    __model__ = ResaleSegment
    id = fields.Integer()
    start_at = fields.DateTime('%Y-%m-%d %H:%M:%S',
                               required=True,
                               error_messages={'invalid': u"申込開始日時を正しい日時に設定ください。"})
    end_at = fields.DateTime('%Y-%m-%d %H:%M:%S',
                             required=True,
                             error_messages={'invalid': u"申込終了日時を正しい日時に設定ください。"})
    resale_start_at = fields.DateTime('%Y-%m-%d %H:%M:%S',
                               required=False,
                               error_messages={'invalid': u"リセール開始日時を正しい日時に設定ください。"})
    resale_end_at = fields.DateTime('%Y-%m-%d %H:%M:%S',
                             required=False,
                             error_messages={'invalid': u"リセール終了日時を正しい日時に設定ください。"})
    sent_status = fields.Integer(required=False)
    sent_at = fields.DateTime('%Y-%m-%d %H:%M:%S',
                             required=False,
                             error_messages={'invalid': u"連携日時を正しい日時に設定ください。"})

    @validates_schema
    def validate_start_and_end_at(self, data):
        if data['start_at'] > data['end_at']:
            raise ValidationError(u'申込開始日時を申込終了日時より前に設定ください。', ['start_at'])

    @validates_schema
    def validate_resale_start_and_end_at(self, data):
        _resale_start_at = data['resale_start_at']
        _resale_end_at = data['resale_end_at']

        if _resale_start_at is None and _resale_end_at is None:
            return True

        if _resale_start_at > _resale_end_at:
            raise ValidationError(u'リセール開始日時をリセール終了日より前に設定ください。')



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
