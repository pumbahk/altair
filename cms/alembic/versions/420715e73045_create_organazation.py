"""create organazation

Revision ID: 420715e73045
Revises: 4a4b099885d2
Create Date: 2012-07-03 12:20:59.482404

"""

# revision identifiers, used by Alembic.
revision = '420715e73045'
down_revision = '4a4b099885d2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('organization',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('backend_id', sa.Integer(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('name', sa.Unicode(length=255), nullable=True),
                    sa.Column('auth_source', sa.String(length=255), nullable=False),
                    sa.Column('prefecture', sa.Unicode(length=255), nullable=True),
                    sa.Column('address', sa.Unicode(length=255), nullable=True),
                    sa.Column('email', sa.String(length=255), nullable=True),
                    sa.Column('contract_status', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
    )

    op.add_column('asset', sa.Column('organization_id', sa.Integer(), nullable=True, index=True))
    op.execute("ALTER TABLE asset ADD INDEX asset_organization_idx(organization_id);")
    op.add_column('assettag', sa.Column('organization_id', sa.Integer(), nullable=True, index=True))
    op.execute("ALTER TABLE assettag ADD INDEX assettag_organization_idx(organization_id);")
    op.add_column('category', sa.Column('organization_id', sa.Integer(), nullable=True, index=True))
    op.execute("ALTER TABLE category ADD INDEX category_organization_idx(organization_id);")
    op.add_column('event', sa.Column('organization_id', sa.Integer(), nullable=True, index=True))
    op.execute("ALTER TABLE event ADD INDEX event_organization_idx(organization_id);")
    op.add_column('flash_asset', sa.Column('organization_id', sa.Integer(), nullable=True, index=True))
    op.execute("ALTER TABLE flash_asset ADD INDEX flash_asset_organization_idx(organization_id);")
    op.add_column('hotword', sa.Column('organization_id', sa.Integer(), nullable=True, index=True))
    op.execute("ALTER TABLE hotword ADD INDEX hotword_organization_idx(organization_id);")
    op.add_column('image_asset', sa.Column('organization_id', sa.Integer(), nullable=True, index=True))
    op.execute("ALTER TABLE image_asset ADD INDEX image_asset_organization_idx(organization_id);")
    op.add_column('layout', sa.Column('organization_id', sa.Integer(), nullable=True, index=True))
    op.execute("ALTER TABLE layout ADD INDEX layout_organization_idx(organization_id);")
    op.add_column('movie_asset', sa.Column('organization_id', sa.Integer(), nullable=True, index=True))
    op.execute("ALTER TABLE movie_asset ADD INDEX movie_asset_organization_idx(organization_id);")
    op.add_column('operator', sa.Column('organization_id', sa.Integer(), nullable=True, index=True))
    op.execute("ALTER TABLE operator ADD INDEX operator_organization_idx(organization_id);")
    op.add_column('page', sa.Column('organization_id', sa.Integer(), nullable=True, index=True))
    op.execute("ALTER TABLE page ADD INDEX page_organization_idx(organization_id);")
    op.add_column('page_accesskeys', sa.Column('organization_id', sa.Integer(), nullable=True, index=True))
    op.execute("ALTER TABLE page_accesskeys ADD INDEX page_accesskeys_organization_idx(organization_id);")
    op.add_column('pagesets', sa.Column('organization_id', sa.Integer(), nullable=True, index=True))
    op.execute("ALTER TABLE pagesets ADD INDEX pagesets_organization_idx(organization_id);")
    op.add_column('pagetag', sa.Column('organization_id', sa.Integer(), nullable=True, index=True))
    op.execute("ALTER TABLE pagetag ADD INDEX pagetag_organization_idx(organization_id);")
    op.add_column('topcontent', sa.Column('organization_id', sa.Integer(), nullable=True, index=True))
    op.execute("ALTER TABLE topcontent ADD INDEX topcontent_organization_idx(organization_id);")
    op.add_column('topic', sa.Column('organization_id', sa.Integer(), nullable=True, index=True))
    op.execute("ALTER TABLE topic ADD INDEX topic_organization_idx(organization_id);")
    op.add_column('promotion', sa.Column('organization_id', sa.Integer(), nullable=True, index=True))
    op.execute("ALTER TABLE promotion ADD INDEX promotion_organization_idx(organization_id);")
    op.add_column('promotion_unit', sa.Column('organization_id', sa.Integer(), nullable=True, index=True))
    op.execute("ALTER TABLE promotion_unit ADD INDEX promotion_unit_organization_idx(organization_id);")
    op.add_column('widgetdisposition', sa.Column('organization_id', sa.Integer(), nullable=True, index=True))
    op.execute("ALTER TABLE widgetdisposition ADD INDEX widgetdisposition_organization_idx(organization_id);")


def downgrade():
    op.drop_table('organization')
    op.drop_column('asset', 'organization_id')
    op.drop_column('assettag', 'organization_id')
    op.drop_column('category', 'organization_id')
    op.drop_column('event', 'organization_id')
    op.drop_column('flash_asset', 'organization_id')
    op.drop_column('hotword', 'organization_id')
    op.drop_column('image_asset', 'organization_id')
    op.drop_column('layout', 'organization_id')
    op.drop_column('movie_asset', 'organization_id')
    op.drop_column('operator', 'organization_id')
    op.drop_column('page', 'organization_id')
    op.drop_column('page_accesskeys', 'organization_id')
    op.drop_column('pagesets', 'organization_id')
    op.drop_column('pagetag', 'organization_id')
    op.drop_column('topcontent', 'organization_id')
    op.drop_column('topic', 'organization_id')
    op.drop_column('promotion', 'organization_id')
    op.drop_column('promotion_unit', 'organization_id')
    op.drop_column('widgetdisposition', 'organization_id')


