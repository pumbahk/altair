"""create mobiletag table

Revision ID: 12c784295a2e
Revises: fb4ae35353d
Create Date: 2013-04-09 15:36:49.418847

"""

# revision identifiers, used by Alembic.
revision = '12c784295a2e'
down_revision = '5091cb8e6bf5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('mobiletag',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('label', sa.Unicode(length=255), nullable=True),
                    sa.Column('publicp', sa.Boolean(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('organization_id', sa.Integer(), nullable=True),
                    sa.CheckConstraint('TODO'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('label','publicp'),
    )
    op.execute("ALTER TABLE mobiletag ADD INDEX mobiletag_organization_idx(organization_id);")

def downgrade():
    op.drop_table("mobiletag")
