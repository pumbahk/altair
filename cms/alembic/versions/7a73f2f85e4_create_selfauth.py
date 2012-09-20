"""create selfauth

Revision ID: 7a73f2f85e4
Revises: 2c539d7ad55e
Create Date: 2012-09-20 17:15:03.286281

"""

# revision identifiers, used by Alembic.
revision = '7a73f2f85e4'
down_revision = '2c539d7ad55e'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('operator_selfauth',
                    sa.Column('operator_id', sa.Integer(), nullable=False),
                    sa.Column('password', sa.String(length=64), nullable=True),
                    sa.ForeignKeyConstraint(['operator_id'], ['operator.id'], name="operator_selfauth_ibfk_1"),
                    sa.PrimaryKeyConstraint('operator_id')
                    )

def downgrade():
    op.drop_constraint("operator_selfauth_ibfk_1", "operator_selfauth", type="foreignkey")
    op.drop_table('operator_selfauth')
