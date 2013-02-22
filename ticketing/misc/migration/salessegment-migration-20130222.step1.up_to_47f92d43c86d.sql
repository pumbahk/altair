-- 作業用カラム
ALTER TABLE Product ADD COLUMN base_product_id BIGINT;

-- alembic 47f92d43c86d まで適用後に以下のデータ作成を行う
-- 移行用新販売区分を作成
INSERT INTO SalesSegment
(
id,start_at,end_at,upper_limit,seat_choice,public,performance_id,sales_segment_group_id
)
SELECT 
id,start_at,end_at,upper_limit,seat_choice,0,NULL AS performance_id, id as sales_segment_group_id
FROM SalesSegmentGroup as ssg
WHERE ssg.id NOT IN (SELECT id FROM SalesSegment);

UPDATE Cart SET sales_segment_id=sales_segment_group_id WHERE sales_segment_id IS NULL;
