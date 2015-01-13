INSERT INTO OrderedProductItemToken (serial, seat_id, ordered_product_item_id, valid) SELECT (tmp_opi_seat.id-tmp_opi_seat_group.first_id_in_group) serial, tmp_opi_seat.seat_id, tmp_opi_seat.ordered_product_item_id, 1 FROM tmp_opi_seat JOIN tmp_opi_seat_group ON tmp_opi_seat.ordered_product_item_id=tmp_opi_seat_group.ordered_product_item_id WHERE tmp_opi_seat_group.existing=0;

