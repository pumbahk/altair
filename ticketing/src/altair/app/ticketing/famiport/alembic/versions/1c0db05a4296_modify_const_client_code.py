# -*- coding: utf-8 -*-
"""modify_const_client_code

Revision ID: 1c0db05a4296
Revises: 3c57098f1687
Create Date: 2015-08-18 20:30:17.191219

"""

# revision identifiers, used by Alembic.
revision = '1c0db05a4296'
down_revision = '3c57098f1687'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text  # noqa
from sqlalchemy.sql import functions as sqlf  # noqa

Identifier = sa.BigInteger


def upgrade():
    op.drop_constraint('code_1', 'FamiPortEvent', type='unique')
    op.create_unique_constraint('code_1', 'FamiPortEvent', ['client_code', 'code_1', 'code_2', 'revision'])


def downgrade():
    op.drop_constraint('famiportevent_ibfk_2', 'FamiPortEvent', type='foreignkey')
    op.drop_constraint('code_1', 'FamiPortEvent', type='unique')
    op.create_foreign_key('famiportevent_ibfk_2', 'FamiPortEvent', 'FamiPortClient', ['client_code'], ['code'])
    op.create_unique_constraint('code_1', 'FamiPortEvent', ['code_1', 'code_2', 'revision'])
