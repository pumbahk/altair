"""insert site,client data

Revision ID: 45e4046d6963
Revises: 152b9d4cf2a4
Create Date: 2012-06-08 17:03:48.312461

"""

# revision identifiers, used by Alembic.
revision = '45e4046d6963'
down_revision = '152b9d4cf2a4'

import sqlahelper
from altaircms.auth.models import Organization

DBSession = sqlahelper.get_session()

def upgrade():
    organization = Organization(
        id = 1,
        name = u"master",
        prefecture = u"tokyo",
        address = u"000",
        email = "foo@example.jp",
        contract_status = 0
        )

    DBSession.add(organization)

    import transaction 
    transaction.commit()



def downgrade():
    Organization.query.delete()
    import transaction 

    transaction.commit()

