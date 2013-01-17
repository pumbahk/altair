"""rename cart tables

Revision ID: 50786ebea789
Revises: d68afc2a0ee
Create Date: 2013-01-15 01:03:13.506690

"""

# revision identifiers, used by Alembic.
revision = '50786ebea789'
down_revision = 'd68afc2a0ee'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute('''
CREATE TABLE `Cart` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `cart_session_id` varchar(255) DEFAULT NULL,
    `performance_id` bigint(20) DEFAULT NULL,
    `system_fee` decimal(16,2) DEFAULT NULL,
    `created_at` datetime DEFAULT NULL,
    `updated_at` datetime DEFAULT NULL,
    `deleted_at` datetime DEFAULT NULL,
    `finished_at` datetime DEFAULT NULL,
    `shipping_address_id` bigint(20) DEFAULT NULL,
    `payment_delivery_method_pair_id` bigint(20) DEFAULT NULL,
    `order_id` bigint(20) DEFAULT NULL,
    `sales_segment_id` bigint(20) DEFAULT NULL,
    `order_no` varchar(255) DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `cart_session_id` (`cart_session_id`),
    KEY `performance_id` (`performance_id`),
    KEY `shipping_address_id` (`shipping_address_id`),
    KEY `payment_delivery_method_pair_id` (`payment_delivery_method_pair_id`),
    KEY `Cart_ibfk_4` (`order_id`),
    KEY `Cart_ibfk_5` (`sales_segment_id`),
    CONSTRAINT `Cart_ibfk_1` FOREIGN KEY (`performance_id`) REFERENCES `Performance` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
    CONSTRAINT `Cart_ibfk_2` FOREIGN KEY (`shipping_address_id`) REFERENCES `ShippingAddress` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
    CONSTRAINT `Cart_ibfk_3` FOREIGN KEY (`payment_delivery_method_pair_id`) REFERENCES `PaymentDeliveryMethodPair` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
    CONSTRAINT `Cart_ibfk_4` FOREIGN KEY (`order_id`) REFERENCES `Order` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
    CONSTRAINT `Cart_ibfk_5` FOREIGN KEY (`sales_segment_id`) REFERENCES `SalesSegmentGroup` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    ''')

    op.execute('''
CREATE TABLE `CartedProduct` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `quantity` int(11) DEFAULT NULL,
    `cart_id` bigint(20) DEFAULT NULL,
    `product_id` bigint(20) DEFAULT NULL,
    `created_at` datetime DEFAULT NULL,
    `updated_at` datetime DEFAULT NULL,
    `deleted_at` datetime DEFAULT NULL,
    `finished_at` datetime DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `product_id` (`product_id`),
    KEY `CartedProduct_ibfk_1` (`cart_id`),
    CONSTRAINT `CartedProduct_ibfk_1` FOREIGN KEY (`cart_id`) REFERENCES `Cart` (`id`),
    CONSTRAINT `CartedProduct_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `Product` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    ''')

    op.execute('''
CREATE TABLE `CartedProductItem` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `quantity` int(11) DEFAULT NULL,
    `product_item_id` bigint(20) DEFAULT NULL,
    `carted_product_id` bigint(20) DEFAULT NULL,
    `created_at` datetime DEFAULT NULL,
    `updated_at` datetime DEFAULT NULL,
    `deleted_at` datetime DEFAULT NULL,
    `finished_at` datetime DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `product_item_id` (`product_item_id`),
    KEY `CartedProductItem_ibfk_1` (`carted_product_id`),
    CONSTRAINT `CartedProductItem_ibfk_1` FOREIGN KEY (`carted_product_id`) REFERENCES `CartedProduct` (`id`),
    CONSTRAINT `CartedProductItem_ibfk_2` FOREIGN KEY (`product_item_id`) REFERENCES `ProductItem` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    ''')

    op.execute('''
CREATE TABLE `CartedProductItem_Seat` (
    `seat_id` bigint(20) DEFAULT NULL,
    `carted_product_item_id` bigint(20) DEFAULT NULL,
    PRIMARY KEY (seat_id, carted_product_item_id),
    KEY `carted_product_item_id` (`carted_product_item_id`),
    KEY `CartedProductItem_Seat_ibfk_1` (`carted_product_item_id`),
    CONSTRAINT `CartedProductItem_Seat_ibfk_1` FOREIGN KEY (`carted_product_item_id`) REFERENCES `CartedProductItem` (`id`),
    CONSTRAINT `CartedProductItem_Seat_ibfk_2` FOREIGN KEY (`seat_id`) REFERENCES `Seat` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    ''')

    op.execute('''
LOCK TABLES ticketing_carts READ, ticketing_cartedproducts READ, ticketing_cartedproductitems READ, cat_seat READ, Cart WRITE, CartedProduct WRITE, CartedProductItem WRITE, CartedProductItem_Seat WRITE, LotEntry WRITE, Checkout WRITE;
    ''')

    op.execute('''
INSERT INTO Cart SELECT id, cart_session_id, performance_id, system_fee, created_at, updated_at, deleted_at, finished_at, shipping_address_id, payment_delivery_method_pair_id, order_id, sales_segment_id, order_no FROM ticketing_carts;
    ''')

    op.execute('''
INSERT INTO CartedProduct SELECT id, quantity, cart_id, product_id, created_at, updated_at, deleted_at, finished_at FROM ticketing_cartedproducts;
    ''')

    op.execute('''
INSERT INTO CartedProductItem SELECT id, quantity, product_item_id, carted_product_id, created_at, updated_at, deleted_at, finished_at FROM ticketing_cartedproductitems; 
    ''')

    op.execute('''
INSERT INTO CartedProductItem_Seat SELECT seat_id, cartproductitem_id FROM cat_seat;
    ''')

    op.execute('''
ALTER TABLE Checkout DROP FOREIGN KEY Checkout_ibfk_1;
    ''')

    op.execute('''
ALTER TABLE Checkout ADD CONSTRAINT Checkout_ibfk_1 FOREIGN KEY (orderCartId) REFERENCES Cart (id) ON DELETE CASCADE;
    ''')

    op.execute('''
ALTER TABLE LotEntry DROP FOREIGN KEY LotEntry_ibfk_1;
    ''')

    op.execute('''
ALTER TABLE LotEntry ADD CONSTRAINT LotEntry_ibfk_1 FOREIGN KEY (cart_id) REFERENCES Cart (id) ON DELETE CASCADE;
    ''')

    op.execute('''
UNLOCK TABLES;
    ''')

    op.execute('''
DROP TABLE cat_seat, ticketing_cartedproductitems, ticketing_cartedproducts, ticketing_carts;
    ''')


def downgrade():
    op.execute('''
CREATE TABLE `ticketing_carts` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `cart_session_id` varchar(255) DEFAULT NULL,
    `performance_id` bigint(20) DEFAULT NULL,
    `system_fee` decimal(16,2) DEFAULT NULL,
    `created_at` datetime DEFAULT NULL,
    `updated_at` datetime DEFAULT NULL,
    `deleted_at` datetime DEFAULT NULL,
    `finished_at` datetime DEFAULT NULL,
    `shipping_address_id` bigint(20) DEFAULT NULL,
    `payment_delivery_method_pair_id` bigint(20) DEFAULT NULL,
    `order_id` bigint(20) DEFAULT NULL,
    `sales_segment_id` bigint(20) DEFAULT NULL,
    `order_no` varchar(255) DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `cart_session_id` (`cart_session_id`),
    KEY `performance_id` (`performance_id`),
    KEY `shipping_address_id` (`shipping_address_id`),
    KEY `payment_delivery_method_pair_id` (`payment_delivery_method_pair_id`),
    KEY `ticketing_carts_ibfk_4` (`order_id`),
    KEY `ticketing_carts_ibfk_5` (`sales_segment_id`),
    CONSTRAINT `ticketing_carts_ibfk_1` FOREIGN KEY (`performance_id`) REFERENCES `Performance` (`id`),
    CONSTRAINT `ticketing_carts_ibfk_2` FOREIGN KEY (`shipping_address_id`) REFERENCES `ShippingAddress` (`id`),
    CONSTRAINT `ticketing_carts_ibfk_3` FOREIGN KEY (`payment_delivery_method_pair_id`) REFERENCES `PaymentDeliveryMethodPair` (`id`),
    CONSTRAINT `ticketing_carts_ibfk_4` FOREIGN KEY (`order_id`) REFERENCES `Order` (`id`),
    CONSTRAINT `ticketing_carts_ibfk_5` FOREIGN KEY (`sales_segment_id`) REFERENCES `SalesSegmentGroup` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    ''')

    op.execute('''
CREATE TABLE `ticketing_cartedproducts` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `quantity` int(11) DEFAULT NULL,
    `cart_id` bigint(20) DEFAULT NULL,
    `product_id` bigint(20) DEFAULT NULL,
    `created_at` datetime DEFAULT NULL,
    `updated_at` datetime DEFAULT NULL,
    `deleted_at` datetime DEFAULT NULL,
    `finished_at` datetime DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `product_id` (`product_id`),
    KEY `ticketing_cartedproducts_ibfk_1` (`cart_id`),
    CONSTRAINT `ticketing_cartedproducts_ibfk_1` FOREIGN KEY (`cart_id`) REFERENCES `ticketing_carts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    ''')

    op.execute('''
CREATE TABLE `ticketing_cartedproductitems` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `quantity` int(11) DEFAULT NULL,
    `product_item_id` bigint(20) DEFAULT NULL,
    `carted_product_id` bigint(20) DEFAULT NULL,
    `created_at` datetime DEFAULT NULL,
    `updated_at` datetime DEFAULT NULL,
    `deleted_at` datetime DEFAULT NULL,
    `finished_at` datetime DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `product_item_id` (`product_item_id`),
    KEY `ticketing_cartedproductitems_ibfk_1` (`carted_product_id`),
    CONSTRAINT `ticketing_cartedproductitems_ibfk_1` FOREIGN KEY (`carted_product_id`) REFERENCES `ticketing_cartedproducts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    ''')

    op.execute('''
CREATE TABLE `cat_seat` (
    `seat_id` bigint(20) DEFAULT NULL,
    `cartproductitem_id` bigint(20) DEFAULT NULL,
    KEY `seat_id` (`seat_id`),
    KEY `cat_seat_ibfk_1` (`cartproductitem_id`),
    CONSTRAINT `cat_seat_ibfk_1` FOREIGN KEY (`cartproductitem_id`) REFERENCES `ticketing_cartedproductitems` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ''')

    op.execute('''
LOCK TABLES Cart READ, CartedProduct READ, CartedProductItem READ, CartedProductItem_Seat READ, ticketing_carts WRITE, ticketing_cartedproducts WRITE, ticketing_cartedproductitems WRITE, cat_seat WRITE, LotEntry WRITE, Checkout WRITE;
    ''')

    op.execute('''
INSERT INTO ticketing_carts SELECT id, cart_session_id, performance_id, system_fee, created_at, updated_at, deleted_at, finished_at, shipping_address_id, payment_delivery_method_pair_id, order_id, sales_segment_id, order_no FROM Cart;
    ''')

    op.execute('''
INSERT INTO ticketing_cartedproducts SELECT id, quantity, cart_id, product_id, created_at, updated_at, deleted_at, finished_at FROM CartedProduct;
    ''')

    op.execute('''
INSERT INTO ticketing_cartedproductitems SELECT id, quantity, product_item_id, carted_product_id, created_at, updated_at, deleted_at, finished_at FROM CartedProductItem;
    ''')

    op.execute('''
INSERT INTO cat_seat SELECT seat_id, carted_product_item_id FROM CartedProductItem_Seat;
    ''')

    op.execute('''
ALTER TABLE Checkout DROP FOREIGN KEY Checkout_ibfk_1;
    ''')

    op.execute('''
ALTER TABLE Checkout ADD CONSTRAINT Checkout_ibfk_1 FOREIGN KEY (orderCartId) REFERENCES ticketing_carts (id) ON DELETE CASCADE;
    ''')

    op.execute('''
ALTER TABLE LotEntry DROP FOREIGN KEY LotEntry_ibfk_1;
    ''')

    op.execute('''
ALTER TABLE LotEntry ADD CONSTRAINT LotEntry_ibfk_1 FOREIGN KEY (cart_id) REFERENCES ticketing_carts (id) ON DELETE CASCADE;
    ''')

    op.execute('''
UNLOCK TABLES;
    ''')

    op.execute('''
DROP TABLE CartedProductItem_Seat, CartedProductItem, CartedProduct, Cart;
    ''')

