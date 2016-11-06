var user_handler = function(u, p) {
  return {
    open_id: 'https://myid.rakuten.co.jp/openid/user/Hpv5eXl5JI8CrYM3P5yjcQ==',
    basic: [ "emailAddress:dev@ticketstar.jp", "nickName:", "firstName:太郎", "lastName:チケスタ", "firstNameKataKana:タロウ", "lastNameKataKana:チケスタ", "birthDay:1999/12/31", "sex:男性" ],
    point: [ "pointAccount:0000-0000-0000-0002" ],
    contact: [ "zip:158-0094", "city:世田谷区", "street:1-14-1", "prefecture:東京都", "tel:050-5830-6868" ]
  };
};

module.exports = user_handler;
