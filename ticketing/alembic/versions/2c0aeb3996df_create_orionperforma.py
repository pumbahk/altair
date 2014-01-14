"""create OrionPerformance table

Revision ID: 2c0aeb3996df
Revises: 2c690a7baa2e
Create Date: 2014-01-14 05:35:20.389232

"""

# revision identifiers, used by Alembic.
revision = '2c0aeb3996df'
down_revision = '2c690a7baa2e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'OrionPerformance',
        sa.Column('id', Identifier, nullable=False, primary_key=True),
        sa.Column('performance_id', Identifier, nullable=True),

        sa.Column('instruction_general', sa.UnicodeText),
        sa.Column('instruction_performance', sa.UnicodeText),
        sa.Column('web', sa.Unicode(255), nullable=True),
        sa.Column('header_url', sa.Unicode(255), nullable=True),
        sa.Column('background_url', sa.Unicode(255), nullable=True),
        sa.Column('icon_url', sa.Unicode(255), nullable=True),
        sa.Column('qr_enabled', sa.Boolean),
        sa.Column('pattern', sa.Unicode(255), nullable=True),

        sa.Column('coupon_2_name', sa.Unicode(255), nullable=True),
        sa.Column('coupon_2_qr_enabled', sa.Boolean),
        sa.Column('coupon_2_pattern', sa.Unicode(255), nullable=True),

        sa.Column('created_at', sa.TIMESTAMP(),
                  server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(),
                  server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),

        sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], name="OrionPerformance_Performance_ibfk_1"),
    )

def downgrade():
    op.drop_table('OrionPerformance')

