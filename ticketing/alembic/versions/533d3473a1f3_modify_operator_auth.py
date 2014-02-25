"""modify_operator_auth

Revision ID: 533d3473a1f3
Revises: 14e9e848dc88
Create Date: 2014-02-24 23:33:46.404296

"""

# revision identifiers, used by Alembic.
revision = '533d3473a1f3'
down_revision = '14e9e848dc88'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("ALTER TABLE OperatorAuth MODIFY COLUMN login_id VARCHAR(384) CHARACTER SET 'ascii', DROP FOREIGN KEY OperatorAuth_ibfk_1, DROP PRIMARY KEY")
    op.execute("ALTER TABLE OperatorAuth ADD CONSTRAINT OperatorAuth_ibfk_1 FOREIGN KEY (operator_id) REFERENCES Operator (id) ON DELETE CASCADE ON UPDATE NO ACTION, ADD COLUMN id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY")

def downgrade():
    op.execute("ALTER TABLE OperatorAuth MODIFY COLUMN login_id VARCHAR(32) CHARACTER SET 'utf8', DROP FOREIGN KEY OperatorAuth_ibfk_1, DROP PRIMARY KEY, DROP COLUMN id")
    op.execute("ALTER TABLE OperatorAuth ADD CONSTRAINT OperatorAuth_ibfk_1 FOREIGN KEY (operator_id) REFERENCES Operator (id) ON DELETE CASCADE ON UPDATE NO ACTION, ADD CONSTRAINT PRIMARY KEY (operator_id);")
