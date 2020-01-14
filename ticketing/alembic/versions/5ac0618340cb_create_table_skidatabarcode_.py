"""Create table SkidataBarcode_ProtoOPIToken.

Revision ID: 5ac0618340cb
Revises: 29662c420296
Create Date: 2019-10-29 14:23:49.603167

"""

# revision identifiers, used by Alembic.
revision = '5ac0618340cb'
down_revision = '29662c420296'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('ProtoOPIToken_SkidataBarcode',
                    sa.Column('proto_opi_token_id', Identifier(), nullable=False, primary_key=True),
                    sa.Column('skidata_barcode_id', Identifier(), nullable=False),
                    sa.ForeignKeyConstraint(['proto_opi_token_id'], ['OrderedProductItemToken.id'],
                                            'ProtoOPIToken_SkidataBarcode_ibfk_1', ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['skidata_barcode_id'], ['SkidataBarcode.id'],
                                            'ProtoOPIToken_SkidataBarcode_ibfk_2', ondelete='CASCADE'),
                    )


def downgrade():
    op.drop_table('ProtoOPIToken_SkidataBarcode')
