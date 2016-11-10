var get_query = function(url) {
  var querystring = require('querystring');
  var p = url.indexOf("?");
  return (0 < p) ? querystring.parse(url.substr(p+1)) : { };
};

var macro = function(str, data) {
  return str.replace(/{([^}]+)}/g, function(all, n) {
    return data[n]===undefined ? '' : data[n];
  });
};

var handler = function(req, res) {
  console.log(req.method+" "+req.url);
  console.log(" from " + req.connection.remoteAddress + " " + req.headers['user-agent']);

  this.req = req;
  this.res = res;
  this.query = get_query(req.url);

  this.base = "localhost";
  this.userHandler = function(u, p) { return 'https://myid.rakuten.co.jp/openid/user/123412341234123412341234'; };
  this.sessionHandler = function(s) { return { _id: 'a9999' } };
};

handler.prototype.end = function(code, headers, text, opt) {
  console.log(" => " + code + (opt ? ' '+((opt===true ? text : opt).split(/\n/))[0] : ''));
  this.res.writeHead(code, headers);
  this.res.end(text);
};

handler.prototype.error = function(code) {
  this.end(code, { }, "Error");
};

handler.prototype.redirect = function(location, q, mode) {
  if(q) {
    var base = get_query(location);
    var extend = require("extend");
    
    var querystring = require('querystring');
    var qs = querystring.stringify(extend({ }, base, q));
    
    var p = location.indexOf("?");
    location = ((0 < p) ? location.substr(0, p) : location) + "?" + qs;
  }
  if(mode == 'html') {
	  // TODO: should html escape
    this.end(200, { 'Content-Type': 'text/html; charset=UTF-8' }, '<meta http-equiv="Refresh" content="0; url=' + location + '">', location);
	} else {
		this.end(301, {
			'Location': location
		}, 'Moved.', location);
  }
};

handler.prototype.form = function(action, param) {
  var fs = require('fs');
  var extend = require('extend');
  var h = this;
  fs.readFile('./form.html', 'utf8', function(err, text) {
	  h.end(200, {
		  'Content-Type': 'text/html; charset=UTF-8'
  	}, macro(text, extend({ ACTION: action }, param)));
  });
};

handler.prototype.handle = function() {
	// TODO: check content-type
	if(this.content !== undefined) {
	  var querystring = require('querystring');
		// overwrite query string in location
		this.query = querystring.parse(this.content);
	}

  var url = this.req.url;
  var q = this.query;

  if(url.startsWith('/openid/auth?')) {
    if(q['openid.mode'] == 'checkid_setup') {
      if(!q['internal.id.mode']) {
        console.log('[step 1] redirect to login form');
        return this.redirect(this.base+"/rms/nid/login", {
					'openid.return_to': q['openid.return_to'],
				});
      } else {
        console.log('[step 4]');
        var s = this.sessionHandler(q['dummy_rakuten_token']);
        if(!s) {
          // TODO:
        }
        return this.redirect(this.base+"/openid/auth", {
				  'openid.mode': 'id_res',
					'openid.return_to': q['openid.return_to'],
          'dummy_rakuten_token': s._id
				}, 'html');
      }
    } else if(q['openid.mode'] == 'id_res') {
      console.log('[step 5] redirect to altair');
      var s = this.sessionHandler(q['dummy_rakuten_token']);
      if(!s.user) {
        return this.error(400);
      }
      return this.redirect(this.query['openid.return_to'], {
			 'openid.ns': 'http://specs.openid.net/auth/2.0',
			 'openid.ns.oauth': 'http://specs.openid.net/extenstions/oauth/1.0',
			 'openid.mode': 'id_res',
			 'openid.sig': '5TMDzoTVd53/JI+GtIfD+17Y1qjTT2otzx+LVJlQEMw=',
			 'openid.signed': 'op_endpoint,claimed_id,identity,return_to,response_nonce,assoc_handle,oauth.request_token,oauth.scope',
			 'openid.op_endpoint': this.base+'/openid/auth',
			 'openid.claimed_id': s.user.open_id,
			 'openid.identity': s.user.open_id,
			 'openid.return_to': q['openid.return_to'],
			 'openid.response_nonce': '2016-10-31T04:58:45Z0',
			 'openid.assoc_handle': 'pfklsdajd4f7b1a23cd050b',
			 'openid.oauth.request_token': s._id,
			 'openid.oauth.scope': 'rakutenid_basicinfo,rakutenid_contactinfo,rakutenid_pointaccount'
			});
    } else if(q['openid.mode'] == 'check_authentication') {
      console.log('[step 6] from internal');
      return this.end(200, { 'Content-Type': 'text/plain; charset=UTF-8' }, "is_valid:true");
    }
  }
  if(url.startsWith('/rms/nid/login?')) {
    console.log('[step 2] show login form');
    return this.form(this.base+"/rms/nid/logini", {
		  'RETURN_TO': q['openid.return_to']
		});
  }
  if(url.startsWith('/rms/nid/logini') && this.req.method == 'POST') {
    console.log('[step 3] receive account credential');
    var user = this.userHandler(q['u'], q['p']);
    if(!user) {
      return this.form(this.base+"/rms/nid/logini", {
        'ERROR': 'no such user',
        'WRONG_U': require('escape-html')(q['u']),
        'RETURN_TO': q['openid.return_to']
      });
    }
    var s = this.sessionHandler();
    s.user = user;
    return this.redirect(this.base+"/openid/auth", {
      'openid.return_to': q['openid.return_to'],
      'openid.mode': 'checkid_setup',
      'internal.id.mode': 'auth',
      'dummy_rakuten_token': s._id
    });
  }
  if(url.startsWith('/openid/oauth/accesstoken')) {
    console.log('[step 7] request access token');
    var s = this.sessionHandler(q['oauth_token']);
    return this.end(200, { 'Content-Type': 'text/plain; charset=UTF-8' }, "oauth_token="+s['_id']+"&oauth_token_secret=eab8cec522b992023ebafcba12f8c289", true);
  }
  if(url.startsWith('/openid/oauth/call')) {
    console.log('[step 8] call apis');
    var s = this.sessionHandler(q['oauth_token']);
    var make_response = function(type) {
      var a = ["status_code:SUCCESS"];
      for(var i=0 ; i<s.user[type].length ; i++) {
        a.push(s.user[type][i]);
      }
      return a;
    };
    if(q['rakuten_oauth_api'] == 'rakutenid_basicinfo') {
		  return this.end(200, { 'Content-Type': 'text/plain; charset=UTF-8' }, make_response('basic').join("\r\n"));
    }
    if(q['rakuten_oauth_api'] == 'rakutenid_pointaccount') {
		  return this.end(200, { 'Content-Type': 'text/plain; charset=UTF-8' }, make_response('point').join("\r\n"));
    }
    if(q['rakuten_oauth_api'] == 'rakutenid_contactinfo') {
		  return this.end(200, { 'Content-Type': 'text/plain; charset=UTF-8' }, make_response('contact').join("\r\n"));
    }
  }

	this.end(400, {
		'Content-Type': 'text/plain'
	}, 'Unsupprted');
};

module.exports = handler;
