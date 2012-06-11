# -*- encoding:utf-8 -*-

"""insert default-layout

Revision ID: a47ddbeb352
Revises: 45e4046d6963
Create Date: 2012-06-08 17:23:48.232011

"""

"""
layoutのデータを投入
"""

# revision identifiers, used by Alembic.
revision = 'a47ddbeb352'
down_revision = '45e4046d6963'

from alembic import op
import sqlalchemy as sa
import os.path

from altaircms.scripts.loadfromcsv import load_from_csv
from altaircms.scripts.loadfromcsv import string_to_value as mapper
from altaircms.layout.models import Layout
from altaircms.models import DBSession

"""
csv layout
============
layout
============
id, blocks, client_id, created_at, site_id, template_filename, title, updated_at
"""

class args:
    path = os.path.join( os.path.dirname(__file__), "layout.csv")
    infile = open(path)
    target = "altaircms.layout.models:Layout"
    
def upgrade():
    load_from_csv(mapper, args, session=DBSession)
    import transaction
    transaction.commit()

def downgrade():
    Layout.query.delete()
    import transaction
    transaction.commit()
