def update():
    op.drop_column('Checkout', sa.Column('orderCartId'))
    op.alter_column('Checkout', '_orderCartId',
        new_column_name='orderCartId',
        existing_type=sa.Column(sa.Unicode(255)),
        existing_nullable=False
        )

def downgrade():
    op.alter_column('Checkout', 'orderCartId',
        new_column_name='_orderCartId',
        existing_type=sa.Column(sa.Unicode(255)),
        existing_nullable=False
        )
    op.add_column('Checkout', sa.Column('orderCartId', Identifier(), nullable=True))
    op.execute('UPDATE Checkout JOIN Cart ON Checkout._orderCartId=Cart.order_no SET orderCartId=Cart.id')
