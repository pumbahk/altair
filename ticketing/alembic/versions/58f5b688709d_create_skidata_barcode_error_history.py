"""create_skidata_barcode_error_history

Revision ID: 58f5b688709d
Revises: 1591106d2def
Create Date: 2019-12-23 10:52:36.721563

"""

# revision identifiers, used by Alembic.
revision = '58f5b688709d'
down_revision = '1591106d2def'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('SkidataBarcodeErrorHistory',
                    sa.Column('id', Identifier(), nullable=False, primary_key=True),
                    sa.Column('skidata_barcode_id', Identifier(), nullable=False),
                    sa.Column('type', sa.String(1), nullable=False),
                    sa.Column('number', sa.INT(11), nullable=False),
                    sa.Column('description', sa.String(255), nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['skidata_barcode_id'], ['SkidataBarcode.id'],
                                            'SkidataBarcodeErrorHistory_ibfk_1', ondelete='CASCADE'),
                    )


def downgrade():
    op.drop_table('SkidataBarcodeErrorHistory')
