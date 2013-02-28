"""create topiccore

Revision ID: 4bc26f9dc2a0
Revises: 3624a7d0cf20
Create Date: 2013-02-05 11:37:39.942457

"""

# revision identifiers, used by Alembic.
revision = '4bc26f9dc2a0'
down_revision = '141a155153a3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('topiccore',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('publish_open_on', sa.DateTime(), nullable=True),
                    sa.Column('publish_close_on', sa.DateTime(), nullable=True),
                    sa.Column('display_order', sa.Integer(), nullable=True),
                    sa.Column('is_vetoed', sa.Boolean(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('type', sa.String(length=32), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('topiccoretag',
                    sa.Column('organization_id', sa.Integer(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('label', sa.Unicode(length=255), nullable=True),
                    sa.Column('publicp', sa.Boolean(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('type', sa.String(length=32), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('label','type','organization_id', 'publicp')
                    )
    op.create_table('topiccoretag2topiccore',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('object_id', sa.Integer(), nullable=True),
                    sa.Column('tag_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['object_id'], ['topiccore.id'], ),
                    sa.ForeignKeyConstraint(['tag_id'], ['topiccoretag.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

    ## data migration
    op.execute('INSERT INTO topiccore (id, publish_open_on, publish_close_on, display_order, is_vetoed, created_at, updated_at, type) SELECT id, publish_open_on, publish_close_on, display_order, is_vetoed, created_at, updated_at, "topic" from topic;')
    op.execute('INSERT INTO topiccoretag (organization_id, label, publicp, type) SELECT organization_id, subkind as label, 1 as publicp, "topic" FROM topic GROUP BY organization_id, subkind;')

def downgrade():
    op.drop_table('topiccoretag2topiccore')
    op.drop_table('topiccoretag')
    op.drop_table('topiccore')
