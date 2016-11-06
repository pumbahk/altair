var argv = require('argv');

argv.info('dummy-rakuten');
argv.option({ name: 'port', short: 'p', type: 'int', description: 'port to listen' });
argv.option({ name: 'hostname', short: 'H', type: 'string', description: 'hostname and port for redirection' });
argv.option({ name: 'ssl-key', short: 'k', type: 'string', description: 'key file for https server' });
argv.option({ name: 'ssl-crt', short: 'c', type: 'string', description: 'certificate file for https server' });
var args = argv.run();

var ssl_server_key = args.options['ssl-key'] || 'server_key.pem';
var ssl_server_crt = args.options['ssl-crt'] || 'server_crt.pem';
var port = args.options.port || 8443;
var hostname = (args.options.hostname || 'localhost:'+port).replace(/:443$/, '');

var user_handler = require('./user');

var session_class = require('./session');
var session = new session_class();

var handler_class = require('./handler');

var options = {
	key: require('fs').readFileSync(ssl_server_key),
	cert: require('fs').readFileSync(ssl_server_crt)
};
require('https')
.createServer(options, function(req, res) {
  var handler = new handler_class(req, res);

  handler.base = 'https://' + hostname;
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

console.log('Listening on port '+port);
