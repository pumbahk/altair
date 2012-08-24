BEGIN;
INSERT INTO TicketFormat(id, organization_id, name, data) VALUES (1, 1,
'楽天チケット標準',
'{
  "size": { "width": "177.96mm", "height": "65.04mm" },
  "perforations": {
    "vertical": [ "19.2mm", "148.1mm" ],
    "horizontal": []
  },
  "printable_areas": [
    { "x": "4mm", "y": "3mm", "width": "11.2mm", "height": "59.04mm" },
    { "x": "23.2mm", "y": "3mm", "width": "120.9mm", "height": "59.04mm" },
    { "x": "152.1mm", "y": "3mm", "width": "21.86mm", "height": "59.04mm" }
  ],
  "print_offset": { "x": "0mm", "y": "0mm" }
}
');
INSERT INTO TicketFormat(id, organization_id, name, data) VALUES (2, 1,
'セブン-イレブン旧式',
'{
  "size": { "width": "177.8mm", "height": "58mm" },
  "perforations": {
    "vertical": [ "28.2mm", "139.3mm" ],
    "horizontal": []
  },
  "printable_areas": [
    { "x": "43.8mm", "y": "3mm", "width": "104mm", "height": "52mm" },
    { "x": "144.8mm", "y": "3mm", "width": "30mm", "height": "52mm" }
  ],
  "print_offset": { "x": "17.8mm", "y": "3mm" }
}
');
INSERT INTO TicketFormat(id, organization_id, name, data) VALUES (3, 1,
'セブン-イレブン新式',
'{
  "size": { "width": "165.1mm", "height": "76mm" },
  "perforations": {
    "vertical": [ "128.1mm" ],
    "horizontal": []
  },
  "printable_areas": [
    { "x": "31.1mm", "y": "6.5mm", "width": "93mm", "height": "63mm" },
    { "x": "132.1mm", "y": "6.5mm", "width": "30mm", "height": "63mm" }
  ],
  "print_offset": { "x": "17.8mm", "y": "6.5mm" }
}
');

INSERT INTO TicketFormat_DeliveryMethod(ticket_format_id, delivery_method_id) VALUES (1, 1);
INSERT INTO TicketFormat_DeliveryMethod(ticket_format_id, delivery_method_id) VALUES (2, 2);
INSERT INTO TicketFormat_DeliveryMethod(ticket_format_id, delivery_method_id) VALUES (1, 3);
INSERT INTO TicketFormat_DeliveryMethod(ticket_format_id, delivery_method_id) VALUES (1, 4);
COMMIT;
