# -*- coding:utf-8 -*-
"""create page_access_key

Revision ID: 4a4b099885d2
Revises: 59c7192b3ca5
Create Date: 2012-06-26 16:36:45.618641

"""

# revision identifiers, used by Alembic.
revision = '4a4b099885d2'
down_revision = '59c7192b3ca5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('page_accesskeys',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('page_id', sa.Integer(), nullable=True),
                    sa.Column('name', sa.Unicode(length=255), nullable=True),
                    sa.Column('hashkey', sa.String(length=32), nullable=False),
                    sa.Column('expiredate', sa.DateTime(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['page_id'], ['page.id'], name="fk_page_accesskeys_page_id_to_page_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    ## initializeで定義されている
    # op.add_column(u'page', sa.Column('published', sa.Boolean(), nullable=True))
    op.drop_column(u'page', u'hash_url')


def downgrade():
    op.add_column(u'page', sa.Column(u'hash_url', mysql.VARCHAR(length=32), nullable=True))
    # op.drop_column(u'page', 'published')
    op.execute("alter table page_accesskeys drop foreign key fk_page_accesskeys_page_id_to_page_id;")
    op.drop_table('page_accesskeys')
