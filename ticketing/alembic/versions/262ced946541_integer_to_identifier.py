"""integer to identifier

Revision ID: 262ced946541
Revises: 18090a14e5c0
Create Date: 2012-07-24 15:43:05.675047

"""

# revision identifiers, used by Alembic.
revision = '262ced946541'
down_revision = '18090a14e5c0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy import schema

Identifier = sa.BigInteger

def integer_to_identifier(table, column_name, nullable=False):
    op.alter_column(table, column_name, name=column_name, nullable=nullable, type_=Identifier(), existing_type=sa.Integer(), existing_nullable=nullable)

def identifier_to_integer(table, column_name, nullable=False):
    op.alter_column(table, column_name, name=column_name, nullable=nullable, type_=sa.Integer(), existing_type=Identifier(), existing_nullable=nullable)

constraints = []

def pop_foreign_key(name, source, referent, local_cols, remote_cols, onupdate=None, ondelete=None):
    constraints.append(
        dict(
            name=name,
            source=source,
            referent=referent,
            local_cols=local_cols,
            remote_cols=remote_cols,
            onupdate=onupdate,
            ondelete=ondelete
            )
        )
    op.drop_constraint(name, source, 'foreignkey')

def restore_all_constraints():
    while constraints:
        constraint = constraints.pop()
        op.create_foreign_key(**constraint)

def upgrade():
    integer_to_identifier('OperatorRole_Operator', 'id')
    integer_to_identifier('reserved_number', 'id')
    integer_to_identifier('payment_reserved_number', 'id')
    pop_foreign_key(
        'cat_seat_ibfk_1',
        'cat_seat',
        'ticketing_cartedproductitems',
        ['cartproductitem_id'], ['id']
        )
    integer_to_identifier('cat_seat', 'cartproductitem_id', True)
    pop_foreign_key(
        'ticketing_cartedproductitems_ibfk_1',
        'ticketing_cartedproductitems',
        'ticketing_cartedproducts',
        ['carted_product_id'], ['id']
        )
    integer_to_identifier('ticketing_cartedproductitems', 'carted_product_id', True)
    integer_to_identifier('ticketing_cartedproductitems', 'id')
    pop_foreign_key(
        'ticketing_cartedproducts_ibfk_1',
        'ticketing_cartedproducts',
        'ticketing_carts',
        ['cart_id'], ['id']
        )
    integer_to_identifier('ticketing_cartedproducts', 'cart_id', True)
    integer_to_identifier('ticketing_cartedproducts', 'id')
    integer_to_identifier('ticketing_carts', 'id')
    integer_to_identifier('SejTicket', 'id')
    integer_to_identifier('secure3d_req_enrol_response', 'id')
    integer_to_identifier('secure3d_req_enrol_request', 'id')
    integer_to_identifier('secure3d_req_auth_response', 'id')
    integer_to_identifier('secure3d_req_auth_request', 'id')
    pop_foreign_key(
        'multicheckout_inquiry_response_card_history_ibfk_1',
        'multicheckout_inquiry_response_card_history',
        'multicheckout_inquiry_response_card',
        ['inquiry_id'], ['id']
        )
    integer_to_identifier('multicheckout_inquiry_response_card_history', 'inquiry_id', True)
    integer_to_identifier('multicheckout_inquiry_response_card_history', 'id')
    integer_to_identifier('multicheckout_inquiry_response_card', 'id')
    integer_to_identifier('multicheckout_response_card', 'id')
    integer_to_identifier('multicheckout_request_card', 'id')
    pop_foreign_key(
        'checkoutitem_ibfk_1',
        'CheckoutItem',
        'Checkout',
        ['checkout_id'], ['id']
        )
    integer_to_identifier('CheckoutItem', 'checkout_id', True)
    integer_to_identifier('CheckoutItem', 'id')
    integer_to_identifier('Checkout', 'id')
    integer_to_identifier('BuyerConditionSet', 'id')
    restore_all_constraints()

def downgrade():
    identifier_to_integer('OperatorRole_Operator', 'id')
    identifier_to_integer('reserved_number', 'id')
    identifier_to_integer('payment_reserved_number', 'id')
    pop_foreign_key(
        'cat_seat_ibfk_1',
        'cat_seat',
        'ticketing_cartedproductitems',
        ['cartproductitem_id'], ['id']
        )
    identifier_to_integer('cat_seat', 'cartproductitem_id', True)
    pop_foreign_key(
        'ticketing_cartedproductitems_ibfk_1',
        'ticketing_cartedproductitems',
        'ticketing_cartedproducts',
        ['carted_product_id'], ['id']
        )
    identifier_to_integer('ticketing_cartedproductitems', 'carted_product_id', True)
    identifier_to_integer('ticketing_cartedproductitems', 'id')
    pop_foreign_key(
        'ticketing_cartedproducts_ibfk_1',
        'ticketing_cartedproducts',
        'ticketing_carts',
        ['cart_id'], ['id']
        )
    identifier_to_integer('ticketing_cartedproducts', 'cart_id', True)
    identifier_to_integer('ticketing_cartedproducts', 'id')
    identifier_to_integer('ticketing_carts', 'id')
    identifier_to_integer('SejTicket', 'id')
    identifier_to_integer('secure3d_req_enrol_response', 'id')
    identifier_to_integer('secure3d_req_enrol_request', 'id')
    identifier_to_integer('secure3d_req_auth_response', 'id')
    identifier_to_integer('secure3d_req_auth_request', 'id')
    pop_foreign_key(
        'multicheckout_inquiry_response_card_history_ibfk_1',
        'multicheckout_inquiry_response_card_history',
        'multicheckout_inquiry_response_card',
        ['inquiry_id'], ['id']
        )
    identifier_to_integer('multicheckout_inquiry_response_card_history', 'inquiry_id', True)
    identifier_to_integer('multicheckout_inquiry_response_card_history', 'id')
    identifier_to_integer('multicheckout_inquiry_response_card', 'id')
    identifier_to_integer('multicheckout_response_card', 'id')
    identifier_to_integer('multicheckout_request_card', 'id')
    pop_foreign_key(
        'checkoutitem_ibfk_1',
        'CheckoutItem',
        'Checkout',
        ['checkout_id'], ['id']
        )
    identifier_to_integer('CheckoutItem', 'checkout_id', True)
    identifier_to_integer('CheckoutItem', 'id')
    identifier_to_integer('Checkout', 'id')
    identifier_to_integer('BuyerConditionSet', 'id')
    restore_all_constraints()
