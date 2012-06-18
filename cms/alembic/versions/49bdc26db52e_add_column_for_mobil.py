"""add column for mobile

Revision ID: 49bdc26db52e
Revises: 3375593899c0
Create Date: 2012-06-18 13:34:15.372262

"""

# revision identifiers, used by Alembic.
revision = '49bdc26db52e'
down_revision = '3375593899c0'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('performance', sa.Column('mobile_purchase_link', sa.UnicodeText(), nullable=True))

    op.add_column('topcontent', sa.Column('mobile_link', sa.Unicode(length=255), nullable=True))
    op.add_column('topcontent', sa.Column('mobile_image_asset_id', sa.Integer(), sa.ForeignKey("image_asset.id", use_alter=True, name="topcontent_mobile_image_asset_id_to_image_asset_id_fk"), nullable=True))
    op.execute("alter table topcontent add constraint topcontent_image_asset_id_fk foreign key (mobile_image_asset_id) references image_asset(id);")
    op.add_column('topic', sa.Column('mobile_link', sa.Unicode(length=255), nullable=True))

def downgrade():
    op.drop_column('performance', 'mobile_purchase_link')

    op.execute("alter table topcontent_mobile_image_asset_id_to_image_asset_id_fk;")
    op.drop_column('topcontent', 'mobile_image_asset_id')
    op.drop_column('topcontent', 'mobile_link')

    op.drop_column('topic', 'mobile_link')

