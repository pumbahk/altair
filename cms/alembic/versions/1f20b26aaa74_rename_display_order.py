"""rename_display_order

Revision ID: 1f20b26aaa74
Revises: 4b2e37cab469
Create Date: 2012-08-17 12:58:25.172173

"""

# revision identifiers, used by Alembic.
revision = '1f20b26aaa74'
down_revision = '4b2e37cab469'

from alembic import op


def upgrade():
    op.execute("ALTER TABLE topic CHANGE orderno display_order int(11);")
    op.execute("ALTER TABLE topcontent CHANGE orderno display_order int(11);")
    op.execute("ALTER TABLE promotion CHANGE orderno display_order int(11);")
    op.execute("ALTER TABLE ticket CHANGE orderno display_order int(11);")
    op.execute("ALTER TABLE category CHANGE orderno display_order int(11);")
    op.execute("ALTER TABLE hotword CHANGE orderno display_order int(11);")

def downgrade():
    op.execute("ALTER TABLE topic CHANGE display_order orderno int(11);")
    op.execute("ALTER TABLE topcontent CHANGE display_order orderno int(11);")
    op.execute("ALTER TABLE promotion CHANGE display_order orderno int(11);")
    op.execute("ALTER TABLE ticket CHANGE display_order orderno int(11);")
    op.execute("ALTER TABLE category CHANGE display_order orderno int(11);")
    op.execute("ALTER TABLE hotword CHANGE display_order orderno int(11);")

