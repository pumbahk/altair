"""create mobiletag table

Revision ID: 12c784295a2e
Revises: fb4ae35353d
Create Date: 2013-04-09 15:36:49.418847

"""

# revision identifiers, used by Alembic.
revision = '12c784295a2e'
down_revision = 'fb4ae35353d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('mobiletag',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('tag_id', sa.Integer(), nullable=True),
                    sa.Column('name', sa.Unicode(length=255), nullable=True),
                    sa.Column('display_order', sa.Integer(), nullable=True),
                    sa.Column('enablep', sa.Boolean(), nullable=True),
                    sa.Column('term_begin', sa.DateTime(), nullable=True),
                    sa.Column('term_end', sa.DateTime(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('organization_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['tag_id'], ['pagetag.id'], name="fk_mobiletag_tag_id_to_pagetag_id"),
                    sa.PrimaryKeyConstraint('id')
    )
    op.execute("ALTER TABLE mobiletag ADD INDEX mobiletag_organization_idx(organization_id);")

def downgrade():
    op.drop_table("mobiletag")
