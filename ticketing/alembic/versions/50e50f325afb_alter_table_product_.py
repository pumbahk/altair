"""alter table product add column seat_stock_type_id

Revision ID: 50e50f325afb
Revises: 7fd74bf0044
Create Date: 2012-07-30 13:31:23.556454

"""

# revision identifiers, used by Alembic.
revision = '50e50f325afb'
down_revision = '7fd74bf0044'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger

def upgrade():
    op.add_column('Product', sa.Column('seat_stock_type_id', Identifier(), sa.ForeignKey("StockType.id", use_alter=True, name="fk_product_seat_stock_type_id_to_stock_type_id"), nullable=True))
    op.execute("alter table Product add constraint fk_product_seat_stock_type_id_to_stock_type_id foreign key (seat_stock_type_id) references StockType(id);")
    op.execute("update Product p, ProductItem pi, Stock s, StockType st set p.seat_stock_type_id = st.id where p.id = pi.product_id and pi.stock_id = s.id and s.stock_type_id = st.id and st.type = 0;")

def downgrade():
    op.execute("alter table Product drop foreign key fk_product_seat_stock_type_id_to_stock_type_id;")
    op.drop_column(u'Product', u'seat_stock_type_id')

