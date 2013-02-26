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

-- 販売区分の終了日時がパフォーマンスの終了日時よりも前である場合はそれを修正する
UPDATE SalesSegment, Performance SET SalesSegment.end_at=Performance.end_on
WHERE SalesSegment.performance_id=Performance.id AND Performance.end_on < SaleSegment.end_at;

-- 当日券用の販売区分の日時を修正する (on-the-day 対応)
UPDATE SalesSegment, Performance, SalesSegmentGroup SET SalesSegment.start_at=DATE(Performance.start_on), SalesSegment.end_at=IF(Performance.end_on IS NOT NULL, Performance.end_on, (DATE(Performance.start_on)+INTERVAL 1 DAY-INTERVAL 1 SECOND))
WHERE SalesSegment.performance_id=Performance.id AND SalesSegment.sales_segment_group_id=SalesSegmentGroup.id AND SalesSegment.start_at <= DATE(Performance.start_on) AND SalesSegmentGroup.kind='sales_counter';

-- 一般販売と先行の販売区分の終了日時を前日の23:59:59までにする
UPDATE SalesSegment, Performance, SalesSegmentGroup SET SalesSegment.end_at=DATE(Performance.start_on)-INTERVAL 1 SECOND
WHERE SalesSegment.performance_id=Performance.id AND SalesSegment.sales_segment_group_id=SalesSegmentGroup.id AND SalesSegment.start_at <= DATE(Performance.start_on) AND SalesSegmentGroup.kind IN ('normal', 'early_firstcome', 'other');

UPDATE Cart SET sales_segment_id=sales_segment_group_id WHERE sales_segment_id IS NULL;
