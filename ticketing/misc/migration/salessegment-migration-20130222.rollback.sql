-- （切戻し用）移行用商品オープン
UPDATE Product
SET public = 1
WHERE sales_segment_id = sales_segment_group_id
;
select * from Product WHERE base_product_id IS NULL;

-- （切戻し用）移行用販売区分クローズ
UPDATE SalesSegment
SET deleted_at = NULL
WHERE id = sales_segment_group_id;
