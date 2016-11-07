var user_handler = function(u, p) {
  var users = { };
  var lines = ("" + require('fs').readFileSync('./user.txt')).split(/\n/);
  for(var i=0 ; i<lines.length ; i++) {
    var user_openid = lines[i].split(/ /, 2);
    users[user_openid[0]] = user_openid[1]
  }
  if(!users[u]) {
    console.log("no such user: " + u);
    return null;
  }
  console.log("found user: " + u);
  return {
    open_id: users[u],
    basic: [ "emailAddress:dev-"+u+"@ticketstar.jp", "nickName:", "firstName:"+u+"太郎", "lastName:チケスタ", "firstNameKataKana:タロウ", "lastNameKataKana:チケスタ", "birthDay:1999/12/31", "sex:男性" ],
    point: [ "pointAccount:0000-0000-0000-0002" ],
    contact: [ "zip:158-0094", "city:世田谷区", "street:1-14-1", "prefecture:東京都", "tel:050-5830-6868" ]
  };
};

module.exports = user_handler;
