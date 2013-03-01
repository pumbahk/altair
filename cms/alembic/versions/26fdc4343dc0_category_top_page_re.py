# -*- coding:utf-8 -*-
"""category top page reference in genre

Revision ID: 26fdc4343dc0
Revises: d2aabeee1ce
Create Date: 2013-02-27 14:18:29.774006

"""

# revision identifiers, used by Alembic.
revision = '26fdc4343dc0'
down_revision = 'd2aabeee1ce'

from alembic import op
import sqlalchemy as sa

def upgrade():
    ## defaultはforeign key貼らなくて良いきがしている
    op.add_column('genre', sa.Column('category_top_pageset_id', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('genre', 'category_top_pageset_id')
