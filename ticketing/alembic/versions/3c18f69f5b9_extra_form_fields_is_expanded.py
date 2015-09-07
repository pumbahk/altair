"""Extra_form_fields is expanded

Revision ID: 3c18f69f5b9
Revises: 20f37ac7246d
Create Date: 2015-09-07 15:30:13.644411

"""

# revision identifiers, used by Alembic.
revision = '3c18f69f5b9'
down_revision = '20f37ac7246d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from altair.models import JSONEncodedDict, MutationDict
from sqlalchemy.dialects.mysql import MEDIUMTEXT

Identifier = sa.BigInteger


def upgrade():
    op.alter_column(table_name="SalesSegmentSetting", column_name="extra_form_fields", type_=MEDIUMTEXT(charset='utf8'), nullable=True)
    op.alter_column(table_name="SalesSegmentGroupSetting", column_name="extra_form_fields", type_=MEDIUMTEXT(charset='utf8'), nullable=True)

def downgrade():
    op.alter_column(table_name="SalesSegmentSetting", column_name="extra_form_fields", type_=MutationDict.as_mutable(JSONEncodedDict(16384)), nullable=True)
    op.alter_column(table_name="SalesSegmentGroupSetting", column_name="extra_form_fields", type_=MutationDict.as_mutable(JSONEncodedDict(16384)), nullable=True)
