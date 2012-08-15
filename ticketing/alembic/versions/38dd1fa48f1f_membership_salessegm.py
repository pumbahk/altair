"""membership_salessegment

Revision ID: 38dd1fa48f1f
Revises: 8f5d887d480
Create Date: 2012-08-10 15:13:56.225347

"""

# revision identifiers, used by Alembic.
revision = '38dd1fa48f1f'
down_revision = '8f5d887d480'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger

def upgrade():
    op.create_table('Membership_SalesSegment',
        sa.Column('membership_id', Identifier(), nullable=False),
        sa.Column('sales_segment_id', Identifier(), nullable=False),
        sa.PrimaryKeyConstraint('membership_id', 'sales_segment_id'),
        sa.ForeignKeyConstraint(['membership_id'], ['Membership.id'], 'Membership_SalesSegment_ibfk_1'),
        sa.ForeignKeyConstraint(['sales_segment_id'], ['SalesSegment.id'], 'Membership_SalesSegment_ibfk_2')
        )

def downgrade():
    op.drop_table('Membership_SalesSegment')
