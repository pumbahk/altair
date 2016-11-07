var argv = require('argv');

argv.info('dummy-rakuten');
argv.option({ name: 'port', short: 'p', type: 'int', description: 'port to listen' });
argv.option({ name: 'base', short: 'b', type: 'string', description: 'url prefix for redirection' });
argv.option({ name: 'ssl-key', short: 'k', type: 'string', description: 'key file for https server' });
argv.option({ name: 'ssl-crt', short: 'c', type: 'string', description: 'certificate file for https server' });
var args = argv.run();

var ssl_server_key = args.options['ssl-key'] || 'server_key.pem';
var ssl_server_crt = args.options['ssl-crt'] || 'server_crt.pem';

var user_handler = require('./user');

var session_class = require('./session');
var session = new session_class();

var handler_class = require('./handler');

var options = null;
try {
  options = {
    key: require('fs').readFileSync(ssl_server_key),
    cert: require('fs').readFileSync(ssl_server_crt)
  };
} catch(e) {
  options = null;
}

var port = args.options.port || (options ? 8443 : 8080);
var base = (args.options.base || 'https://localhost:'+port);

var createServer = function(listener) {
  if(options != null) {
    return require('https').createServer(options, listener);
  } else {
    return require('http').createServer(listener);
  }
};

createServer(function(req, res) {
  var handler = new handler_class(req, res);

  handler.base = base;
  handler.userHandler = user_handler;
  handler.sessionHandler = function(token) { return session.handle(token); };

  if(req.method == "POST") {
    var content = "";
    req.on('readable', function(chunk) {
		  content += req.read();
    });
		req.on('end', function() {
		  handler.content = content;
			handler.handle();
		});
	} else {
	  handler.handle();
	}
})
.listen(port);

var server_name = options ? 'HTTPS server' : 'HTTP server';
console.log(server_name + ' is listening on port ' + port);
