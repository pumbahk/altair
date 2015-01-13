DELIMITER //

CREATE TEMPORARY TABLE tmp_opi_seat (id INTEGER NOT NULL AUTO_INCREMENT, seat_id BIGINT, ordered_product_item_id BIGINT, PRIMARY KEY (id), KEY(seat_id), KEY(ordered_product_item_id)) SELECT seat_id, OrderedProductItem_id ordered_product_item_id FROM orders_seat ORDER BY OrderedProductItem_id, seat_id;

DROP PROCEDURE IF EXISTS _tmp_populate_for_quantity_only;
CREATE PROCEDURE _tmp_populate_for_quantity_only()
BEGIN
    DECLARE done BOOL DEFAULT FALSE;
    DECLARE ordered_product_item_id BIGINT DEFAULT NULL;
    DECLARE quantity BIGINT DEFAULT NULL;
    DECLARE i, j INTEGER DEFAULT NULL;
    DECLARE c CURSOR FOR SELECT OrderedProductItem.id, OrderedProductItem.quantity FROM OrderedProductItem JOIN ProductItem ON OrderedProductItem.product_item_id = ProductItem.id JOIN Stock ON ProductItem.stock_id = Stock.id JOIN StockType ON Stock.stock_type_id = StockType.id LEFT JOIN OrderedProductItemToken ON OrderedProductItem.id = OrderedProductItemToken.ordered_product_item_id WHERE StockType.quantity_only <> 0 AND OrderedProductItemToken.id IS NULL;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN c;

    SET j = 0;
    _outer: LOOP
        FETCH c INTO ordered_product_item_id, quantity;
        IF done THEN
            LEAVE _outer;
        END IF;
        SET i = 0;
        WHILE i < quantity DO
            INSERT INTO tmp_opi_seat (seat_id, ordered_product_item_id) VALUES (NULL, ordered_product_item_id);
            SET i = i + 1;
            SET j = j + 1;
        END WHILE;
    END LOOP;
    CLOSE c;
    SELECT j;
END;

CALL _tmp_populate_for_quantity_only();

CREATE TEMPORARY TABLE tmp_opi_seat_group (ordered_product_item_id BIGINT, first_id_in_group BIGINT, existing BOOL, c INTEGER, KEY(ordered_product_item_id), KEY (first_id_in_group)) SELECT tmp_opi_seat.ordered_product_item_id, MIN(tmp_opi_seat.id) first_id_in_group, (OrderedProductItemToken.id IS NOT NULL) existing, COUNT(DISTINCT tmp_opi_seat.seat_id) c FROM tmp_opi_seat LEFT JOIN OrderedProductItemToken ON OrderedProductItemToken.ordered_product_item_id=tmp_opi_seat.ordered_product_item_id GROUP BY tmp_opi_seat.ordered_product_item_id;
DROP PROCEDURE _tmp_populate_for_quantity_only;
//
DELIMITER ;
