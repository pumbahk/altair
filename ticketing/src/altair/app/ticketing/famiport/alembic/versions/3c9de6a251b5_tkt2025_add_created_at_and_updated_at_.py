"""#tkt2025 add created_at_and_updated_at to FamiPortOperator

Revision ID: 3c9de6a251b5
Revises: d068c02f6e6
Create Date: 2016-07-22 19:48:25.423598

"""

# revision identifiers, used by Alembic.
revision = '3c9de6a251b5'
down_revision = 'd068c02f6e6'

from alembic import op
import sqlalchemy as sa
from datetime import datetime
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def fill_email_column():
    conn = op.get_bind()
    res = conn.execute("select user_name, id from FamiPortOperator")
    result = res.fetchall()
    for r in result:
        op.execute("update FamiPortOperator set email='{0}@example.com' where id={1};".format(r[0], r[1]))

def upgrade():
    created_time = sa.func.current_timestamp()

    op.add_column('FamiPortOperator', sa.Column('created_at', sa.DateTime, nullable=False, server_default=created_time))
    op.add_column('FamiPortOperator', sa.Column('updated_at', sa.DateTime, nullable=False, server_default=created_time))
    op.add_column('FamiPortOperator', sa.Column('expired_at', sa.DateTime))
    op.add_column('FamiPortOperator', sa.Column('active', sa.Boolean, server_default=('1')))
    op.add_column('FamiPortOperator', sa.Column('email', sa.Unicode(120), nullable=True))
    fill_email_column()
    op.execute("ALTER TABLE FamiPortOperator ADD UNIQUE (user_name);")
    op.execute("ALTER TABLE FamiPortOperator ADD UNIQUE (email);")
    op.execute("ALTER TABLE FamiPortOperator MODIFY email varchar(120) NOT NULL;")



def downgrade():
    op.execute("alter table FamiPortOperator drop index user_name;")
    op.execute("alter table FamiPortOperator drop index email;")
    op.drop_column(u'FamiPortOperator', 'created_at')
    op.drop_column(u'FamiPortOperator', 'updated_at')
    op.drop_column(u'FamiPortOperator', 'expired_at')
    op.drop_column(u'FamiPortOperator', 'active')
    op.drop_column(u'FamiPortOperator', 'email')
