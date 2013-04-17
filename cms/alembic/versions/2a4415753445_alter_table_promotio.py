"""alter table promotion, topcontent, topic add column mobile_tag_id

Revision ID: 2a4415753445
Revises: 12c784295a2e
Create Date: 2013-04-09 16:43:31.857309

"""

# revision identifiers, used by Alembic.
revision = '2a4415753445'
down_revision = '12c784295a2e'

from alembic import op
import sqlalchemy as sa


def upgrade():

    op.add_column('promotion', sa.Column('mobile_tag_id', sa.Integer(), nullable=True))
    op.add_column('topcontent', sa.Column('mobile_tag_id', sa.Integer(), nullable=True))
    op.add_column('topic', sa.Column('mobile_tag_id', sa.Integer(), nullable=True))

    op.create_foreign_key('fk_promotion_mobile_tag_id_to_mobiletag_id', 'promotion', 'mobiletag', ['mobile_tag_id'], ['id'])
    op.create_foreign_key('fk_topcontent_mobile_tag_id_to_mobiletag_id', 'topcontent', 'mobiletag', ['mobile_tag_id'], ['id'])
    op.create_foreign_key('fk_topic_mobile_tag_id_to_mobiletag_id', 'topic', 'mobiletag', ['mobile_tag_id'], ['id'])

def downgrade():
    op.drop_constraint('fk_promotion_mobile_tag_id_to_mobiletag_id', 'promotion', type='foreignkey')
    op.drop_constraint('fk_topcontent_mobile_tag_id_to_mobiletag_id', 'topcontent', type='foreignkey')
    op.drop_constraint('fk_topic_mobile_tag_id_to_mobiletag_id', 'topic', type='foreignkey')

    op.drop_column('promotion', 'mobile_tag_id')
    op.drop_column('topcontent', 'mobile_tag_id')
    op.drop_column('topic', 'mobile_tag_id')