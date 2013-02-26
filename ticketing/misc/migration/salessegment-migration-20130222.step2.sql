SELECT COUNT(*) FROM Cart LEFT JOIN SalesSegment ON Cart.sales_segment_id=SalesSegment.id WHERE SalesSegment.id IS NULL;

-- 既存商品を移行用販売区分にひもづけ
UPDATE Product
SET sales_segment_id = sales_segment_group_id
WHERE sales_segment_id IS NULL
AND base_product_id IS NULL
;


-- 決済引取方法を移行用販売区分にひもづけ
UPDATE PaymentDeliveryMethodPair
SET sales_segment_id = sales_segment_group_id
WHERE sales_segment_id IS NULL;


-- 新販売区分を作成
INSERT INTO SalesSegment
(
start_at,end_at,upper_limit,seat_choice,public,performance_id,sales_segment_group_id
)
SELECT DISTINCT
start_at,end_at,upper_limit,seat_choice,SalesSegmentGroup.public,Performance.id AS performance_id, SalesSegmentGroup.id as sales_segment_group_id
FROM Performance
JOIN Stock
ON Stock.performance_id = Performance.id
JOIN ProductItem
ON ProductItem.stock_id = Stock.id
AND ProductItem.performance_id = Performance.id
JOIN Product
ON Product.id = ProductItem.product_id
JOIN SalesSegmentGroup
ON SalesSegmentGroup.id = Product.sales_segment_group_id
WHERE Performance.deleted_at IS NULL
AND Stock.deleted_at IS NULL
AND ProductItem.deleted_at IS NULL
AND Product.deleted_at IS NULL
AND SalesSegmentGroup.deleted_at IS NULL
AND SalesSegmentGroup.id IN (SELECT id FROM SalesSegment);


-- ProductをStockから辿れるSalesSegmentにコピーする
INSERT INTO Product
(name, price, sales_segment_group_id, event_id, seat_stock_type_id, display_order, public, description, sales_segment_id, base_product_id, performance_id)
SELECT name, price, Product.sales_segment_group_id, event_id, seat_stock_type_id, display_order, Product.public, description, SalesSegment.id, Product.id, SalesSegment.performance_id
FROM Product
JOIN SalesSegment
ON SalesSegment.sales_segment_group_id = Product.sales_segment_group_id
AND SalesSegment.id != SalesSegment.sales_segment_group_id
WHERE Product.base_product_id IS NULL
AND Product.deleted_at IS NULL;

-- Product以下のProductItemもコピーする

INSERT INTO ProductItem 
(price, product_id, performance_id, stock_id, quantity, ticket_bundle_id, name)
SELECT ProductItem.price, Product.id, ProductItem.performance_id, stock_id, ProductItem.quantity, ticket_bundle_id, ProductItem.name
FROM ProductItem
JOIN Product
ON ProductItem.product_id = Product.base_product_id
AND ProductItem.performance_id = Product.performance_id
AND ProductItem.deleted_at IS NULL
AND Product.deleted_at IS NULL;

-- 決済引取方法
INSERT INTO SalesSegment_PaymentDeliveryMethodPair
(
payment_delivery_method_pair_id, sales_segment_id
)
SELECT PaymentDeliveryMethodPair.id, SalesSegment.id
FROM PaymentDeliveryMethodPair
JOIN SalesSegmentGroup
ON SalesSegmentGroup.id = PaymentDeliveryMethodPair.sales_segment_group_id
JOIN SalesSegment
ON SalesSegment.sales_segment_group_id = SalesSegmentGroup.id
WHERE (PaymentDeliveryMethodPair.id, SalesSegment.id) NOT IN (
    SELECT payment_delivery_method_pair_id, sales_segment_id
    FROM SalesSegment_PaymentDeliveryMethodPair);
-- 移行用商品クローズ
UPDATE Product
SET public = 0
WHERE sales_segment_id = sales_segment_group_id;
;
-- 移行用販売区分クローズ
-- データ移行作業完了後から15分以上経過後に実行
UPDATE SalesSegment
SET deleted_at = CURRENT_TIMESTAMP
WHERE id = sales_segment_group_id
AND id != 1
;
-- id = 1はbooster用に残す

