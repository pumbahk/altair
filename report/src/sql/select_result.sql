/* For dumping the result */

select
    event_id,
    event_name,
    perf_id,
    -- IF(perf_name = 'vs オリックス', 'vs オリックス・バファローズ', perf_name) AS perf_name,
    perf_name,
    start_on,
    channel,
    order_no,
    DATE_FORMAT(ordered_at, '%Y-%m-%d %H:%I') AS ordered_at,
    -- IF(select_type = 'unknown', 'system', select_type) AS select_type,
    ua_type,
    order_status,
    payment_status,
    delivery_status,
    CASE payment_method WHEN 1 THEN 'マルチ決済' WHEN 2 THEN 'ID決済' WHEN 3 THEN 'セブン' WHEN 4 THEN '窓口' WHEN 5 THEN '無料' WHEN 6 THEN 'ファミマ' ELSE '不明' END AS payment,
    CASE delivery_method WHEN 1 THEN '配送' WHEN 2 THEN 'セブン' WHEN 3 THEN '窓口' WHEN 4 THEN 'QR認証' WHEN 5 THEN 'イベントゲート' WHEN 6 THEN' ファミマ' ELSE '不明' END AS delivery,
    fc_type,
    IF(fc_type ='', '', fc_id) AS fc_id,
    total,
    fee,
    qty,
    point,
    -- item_serial,
    item_name,
    item_price,
    1 as item_qty,
    seat_name
from order201605
join order_seat201605 using (order_id)
