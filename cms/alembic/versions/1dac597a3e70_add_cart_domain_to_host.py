"""add_cart_domain_to_host

Revision ID: 1dac597a3e70
Revises: c09a614defd
Create Date: 2015-03-02 23:36:17.900629

"""

# revision identifiers, used by Alembic.
revision = '1dac597a3e70'
down_revision = 'c09a614defd'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('host', sa.Column('cart_domain', sa.Unicode(255)))
    op.execute("""UPDATE host SET cart_domain=CONCAT('https://', host_name) WHERE host_name <> 'ticket.rakuten.co.jp';""")
    op.execute("""UPDATE host SET cart_domain='https://rt.tstar.jp' WHERE host_name = 'ticket.rakuten.co.jp';""")

def downgrade():
    op.drop_column('host', 'cart_domain')
