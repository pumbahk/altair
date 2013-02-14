"""alter table Refund rename colume reason

Revision ID: 368e33588cbe
Revises: 2592c3207571
Create Date: 2013-02-06 13:51:10.427936

"""

# revision identifiers, used by Alembic.
revision = '368e33588cbe'
down_revision = '2592c3207571'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute('ALTER TABLE Refund CHANGE COLUMN reason cancel_reason VARCHAR(255);')

def downgrade():
    op.execute('ALTER TABLE Refund CHANGE COLUMN cancel_reason reason VARCHAR(255);')

