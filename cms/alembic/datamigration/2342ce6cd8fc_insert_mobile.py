"""insert mobile layout

Revision ID: 2342ce6cd8fc
Revises: 3adbb1f00111
Create Date: 2012-06-13 13:27:24.054109

"""

# revision identifiers, used by Alembic.
revision = '2342ce6cd8fc'
down_revision = '3adbb1f00111'

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
    path = os.path.join( os.path.dirname(__file__), "layout.mobile.csv")
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
