-- 自由席はまだ無い。
select opi.* from `Order` as o 
join PaymentDeliveryMethodPair as pdm on o.payment_delivery_method_pair_id = pdm.id 
join DeliveryMethod as dm on pdm.delivery_method_id = dm.id 
join OrderedProduct as op on o.id = op.order_id 
join OrderedProductItem as opi on opi.ordered_product_id = op.id 
join orders_seat as xx on opi.id = xx.OrderedProductItem_id 
join Seat as s on xx.seat_id = s.id 
join Product as p on op.product_id = p.id 
join StockType as st on p.seat_stock_type_id = st.id 
where dm.delivery_plugin_id = 4 and st.type = 0
