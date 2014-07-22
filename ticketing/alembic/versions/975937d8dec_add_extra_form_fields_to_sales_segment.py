"""add_extra_form_fields_to_sales_segment

Revision ID: 975937d8dec
Revises: 2c46064b0c0a
Create Date: 2014-07-13 23:09:21.972362

"""

# revision identifiers, used by Alembic.
revision = '975937d8dec'
down_revision = '2c46064b0c0a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from altair.models import JSONEncodedDict, MutationDict

Identifier = sa.BigInteger


def upgrade():
    op.add_column('SalesSegmentGroupSetting', sa.Column('extra_form_fields', MutationDict.as_mutable(JSONEncodedDict(16384))))
    op.add_column('SalesSegmentSetting', sa.Column('extra_form_fields', MutationDict.as_mutable(JSONEncodedDict(16384))))
    op.add_column('SalesSegmentSetting', sa.Column('use_default_extra_form_fields', sa.Boolean()))

def downgrade():
    op.drop_column('SalesSegmentGroupSetting', 'extra_form_fields')
    op.drop_column('SalesSegmentSetting', 'extra_form_fields')
    op.drop_column('SalesSegmentSetting', 'use_default_extra_form_fields')
