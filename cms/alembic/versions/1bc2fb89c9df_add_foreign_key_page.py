"""create table MobileTag2PageSet

Revision ID: 1bc2fb89c9df
Revises: 2a4415753445
Create Date: 2013-04-10 11:26:35.316067

"""

# revision identifiers, used by Alembic.
revision = '1bc2fb89c9df'
down_revision = '2a4415753445'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('mobiletag2pageset',
                    sa.Column('object_id', sa.Integer(), nullable=True),
                    sa.Column('tag_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['object_id'], ['pagesets.id'], ),
                    sa.ForeignKeyConstraint(['tag_id'], ['mobiletag.id'], ),
                    sa.PrimaryKeyConstraint('object_id', "tag_id")
    )

def downgrade():
    op.drop_table("mobiletag2pageset")
