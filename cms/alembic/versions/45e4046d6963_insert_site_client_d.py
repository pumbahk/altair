"""insert site,client data

Revision ID: 45e4046d6963
Revises: 152b9d4cf2a4
Create Date: 2012-06-08 17:03:48.312461

"""

# revision identifiers, used by Alembic.
revision = '45e4046d6963'
down_revision = '152b9d4cf2a4'

from alembic import op
import sqlalchemy as sa

import sqlahelper
from altaircms.models import Site
from altaircms.auth.models import Client

DBSession = sqlahelper.get_session()

def upgrade():
    client = Client(
        id = 1,
        name = u"master",
        prefecture = u"tokyo",
        address = u"000",
        email = "foo@example.jp",
        contract_status = 0
        )

    site = Site(name=u"ticketstar",
                description=u"ticketstar ticketstar",
                url="http://example.com",
                client=client)

    DBSession.add(client)
    DBSession.add(site)

    import transaction 
    transaction.commit()



def downgrade():
    import transaction 

    Site.query.delete()
    transaction.commit()

    Client.query.delete()
    transaction.commit()

