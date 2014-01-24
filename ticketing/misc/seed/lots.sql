set @organization_id = 1;
set @account_id = 1;

INSERT INTO Site (
name, zip, prefecture, city, street, other_address, tel_1, tel_2, fax, drawing_url, metadata_url
) VALUES (
'テストサイト', '1234567', '東京都', '千代田区', '千代田1丁目', NULL, NULL, NULL, NULL, NULL, NULL
)
;

SET @site_id = (select last_insert_id() from Site limit 1);

INSERT INTO Event (
code, title,abbreviated_title,account_id,organization_id)
VALUES
(
'TEST89LOT','抽選イベント','抽選イベント', @account_id, @organization_id
);

SET @event_id = (select last_insert_id() from Event limit 1);

INSERT INTO SalesSegment (
name, kind, start_at, end_at, upper_limit, seat_choice, event_id, public
) VALUES (
'抽選テスト区分', 'lot', '2012/12/01', '2012/12/09', 10, 0, @event_id, 1
);

SET @sales_segment_id = (select last_insert_id() from SalesSegment limit 1);


INSERT INTO Lot (
name, limit_wishes, event_id, selection_type, sales_segment_id, status
) VALUES (
'テスト抽選', 3, @event_id, 0, @sales_segment_id, NULL
);

SET @lot_id = (select last_insert_id() from Lot limit 1);


-- *********************************
-- テスト公演１
-- *********************************

INSERT INTO Performance (
name, code, open_on, start_on, end_on, event_id
) VALUES (
'テスト公演１', 'test-01', '2012/12/10 10:00:00', '2012/12/10 11:00:00', '2012/12/10 15:00:00', @event_id
);

SET @performance_id = (select last_insert_id() from Performance limit 1);


INSERT INTO Venue (
site_id, performance_id, organization_id, name, sub_name, attributes
) VALUES (
@site_id, @performance_id, 1, '会場１', '会場１', NULL
);

INSERT INTO Lots_Performance (
lot_id, performance_id
) VALUES (
@lot_id, @performance_id
);


-- *********************************
-- テスト公演２
-- *********************************

INSERT INTO Performance (
name, code, open_on, start_on, end_on, event_id
) VALUES (
'テスト公演２', 'test-02', '2012/12/10 10:00:00', '2012/12/10 11:00:00', '2012/12/10 15:00:00', @event_id
);


SET @performance_id = (select last_insert_id() from Performance limit 1);


INSERT INTO Venue (
site_id, performance_id, organization_id, name, sub_name, attributes
) VALUES (
@site_id, @performance_id, @organization_id, '会場２', '会場２', NULL
);


INSERT INTO Lots_Performance (
lot_id, performance_id
) VALUES (
@lot_id, @performance_id
);


-- *********************************
-- テスト公演３
-- *********************************

INSERT INTO Performance (
name, code, open_on, start_on, end_on, event_id
) VALUES (
'テスト公演３', 'test-03', '2012/12/10 10:00:00', '2012/12/10 11:00:00', '2012/12/10 15:00:00', @event_id
);

SET @performance_id = (select last_insert_id() from Performance limit 1);


INSERT INTO Venue (
site_id, performance_id, organization_id, name, sub_name, attributes
) VALUES (
@site_id, @performance_id, @organization_id, '会場３', '会場３', NULL
);

INSERT INTO Lots_Performance (
lot_id, performance_id
) VALUES (
@lot_id, @performance_id
);


-- *********************************
-- テスト公演４
-- *********************************

INSERT INTO Performance (
name, code, open_on, start_on, end_on, event_id
) VALUES (
'テスト公演４', 'test-04', '2012/12/10 10:00:00', '2012/12/10 11:00:00', '2012/12/10 15:00:00', @event_id
);

SET @performance_id = (select last_insert_id() from Performance limit 1);


INSERT INTO Venue (
site_id, performance_id, organization_id, name, sub_name, attributes
) VALUES (
@site_id, @performance_id, @organization_id, '会場４', '会場４', NULL
);

INSERT INTO Lots_Performance (
lot_id, performance_id
) VALUES (
@lot_id, @performance_id
);




INSERT INTO StockType (
name, type, event_id, quantity_only, style, display_order
) VALUES (
'S席', 0, @event_id, 1, "{}", 1
);

SET @stock_type_id = (select last_insert_id() from StockType limit 1);

INSERT INTO Lots_StockType (
lot_id, stock_type_id
) VALUES (
@lot_id, @stock_type_id
);


INSERT INTO Product (
name, price, sales_segment_id, event_id, seat_stock_type_id, display_order, public
) VALUES (
'S席大人', 1000, @sales_segment_id, @event_id, @stock_type_id, 1, 1
);

INSERT INTO Product (
name, price, sales_segment_id, event_id, seat_stock_type_id, display_order, public
) VALUES (
'S席小人', 800, @sales_segment_id, @event_id, @stock_type_id, 1, 1
);


INSERT INTO StockType (
name, type, event_id, quantity_only, style, display_order
) VALUES (
'A席', 0, @event_id, 1, "{}", 2
);

SET @stock_type_id = (select last_insert_id() from StockType limit 1);

INSERT INTO Lots_StockType (
lot_id, stock_type_id
) VALUES (
@lot_id, @stock_type_id
);


INSERT INTO Product (
name, price, sales_segment_id, event_id, seat_stock_type_id, display_order, public
) VALUES (
'A席大人', 1000, @sales_segment_id, @event_id, @stock_type_id, 1, 1
);

INSERT INTO Product (
name, price, sales_segment_id, event_id, seat_stock_type_id, display_order, public
) VALUES (
'A席小人', 800, @sales_segment_id, @event_id, @stock_type_id, 1, 1
);

select @lot_id;

