"""create table skidata_barcode_email_history.

Revision ID: 294ca5bb74d2
Revises: 5ac0618340cb
Create Date: 2019-11-19 11:26:01.300870

"""

# revision identifiers, used by Alembic.
revision = '294ca5bb74d2'
down_revision = '5ac0618340cb'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('SkidataBarcodeEmailHistory',
                    sa.Column('id', Identifier(), nullable=False, primary_key=True),
                    sa.Column('skidata_barcode_id', Identifier(), nullable=False),
                    sa.Column('to_address', sa.String(255), nullable=False),
                    sa.Column('sent_at', sa.DateTime(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['skidata_barcode_id'], ['SkidataBarcode.id'],
                                            'SkidataBarcodeEmailHistory_ibfk_1', ondelete='CASCADE'),
                    )


def downgrade():
    op.drop_table('SkidataBarcodeEmailHistory')
