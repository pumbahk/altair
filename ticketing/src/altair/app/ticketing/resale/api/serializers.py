# encoding: utf-8

from marshmallow import Schema, fields, validates_schema, ValidationError
from ..models import ResaleSegment, ResaleRequest

class ResaleSegmentSerializer(Schema):
    __model__ = ResaleSegment
    id = fields.Integer()
    start_at = fields.DateTime('%Y-%m-%d %H:%M:%S', required=True)
    end_at = fields.DateTime('%Y-%m-%d %H:%M:%S', required=True)

    @validates_schema
    def valdate_start_and_end_at(self, data):
        if data['start_at'] > data['end_at']:
            raise ValidationError('start_at should be earlier than end_at.', 'start_at')

class ResaleSegmentCreateSerializer(ResaleSegmentSerializer):
    performance_id = fields.Integer(required=True)

class ResaleRequestSerializer(Schema):
    __model__ = ResaleRequest
    id = fields.Integer()
    ordered_product_item_token_id = fields.Integer(required=True)
    bank_code = fields.String(required=True)
    bank_branch_code = fields.String(required=True)
    account_number = fields.String(required=True)
    account_holder_name = fields.String(required=True)
    total_amount = fields.Number(required=True)

class ResaleRequestCreateSerializer(ResaleRequestSerializer):
    performance_id = fields.Integer(required=True)
    resale_segment_id = fields.Integer(required=True)