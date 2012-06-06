"""add url mapping

Revision ID: 513581379efc
Revises: 585370eac7e2
Create Date: 2012-06-05 10:13:44.660024

"""

# revision identifiers, used by Alembic.
revision = '513581379efc'
down_revision = '585370eac7e2'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('page_default_info',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('title_fmt', sa.Unicode(length=255), nullable=True),
                    sa.Column('url_fmt', sa.Unicode(length=255), nullable=True),
                    sa.Column('keywords', sa.Unicode(length=255), nullable=True),
                    sa.Column('description', sa.Unicode(length=255), nullable=True),
                    sa.Column('pageset_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['pageset_id'], ['pagesets.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    
    op.add_column("page", sa.Column("name", sa.Unicode(255)))
    
def downgrade():
    op.drop_table('page_default_info')

    op.drop_column("page", "name")
