"""add static page model

Revision ID: ea688732982
Revises: c5b01852c04
Create Date: 2012-08-06 16:37:23.054062

"""

# revision identifiers, used by Alembic.
revision = 'ea688732982'
down_revision = 'c5b01852c04'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('static_pages',
                    sa.Column('organization_id', sa.Integer(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('name', sa.String(length=255), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

def downgrade():
    op.drop_table('static_pages')
