var session = function() {
  this._session = [ ];
};

session.prototype.handle = function(token) {
  if(token && this._session[token.substr(1)*1]) {
    return this._session[token.substr(1)*1];
  }
  token = "a" + (this._session.length);
  this._session.push({ _id: token });
  return this._session[token.substr(1)*1];
};

module.exports = session;
