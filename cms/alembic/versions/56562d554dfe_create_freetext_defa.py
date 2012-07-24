"""create freetext default body

Revision ID: 56562d554dfe
Revises: 1b83e811f262
Create Date: 2012-07-23 18:48:07.158062

"""

# revision identifiers, used by Alembic.
revision = '56562d554dfe'
down_revision = '1b83e811f262'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('freetext_default',
                    sa.Column('organization_id', sa.Integer(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.Unicode(length=255), nullable=True),
                    sa.Column('text', sa.UnicodeText(), nullable=True),
                    sa.Column('created_by_id', sa.Integer(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

def downgrade():
    op.drop_table('freetext_default')

