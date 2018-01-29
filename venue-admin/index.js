const argv = require('argv');

argv.info('venue-admin');
argv.option({ name: 'port', short: 'p', type: 'int', description: 'port to listen' });
argv.option({ name: 'deploy-dir', short: 'd', type: 'string', description: 'deploy directory' });
argv.option({ name: 'config', short: 'c', type: 'string', description: 'pyramid config file' });
argv.option({ name: 'repos-dir', short: 'r', type: 'string', description: 'svg repos directory' });
argv.option({ name: 'report-to', type: 'string', description: 'receipient email address for report' });
argv.option({ name: 'report-from', type: 'string', description: 'sender email address for report' });
const args = argv.run();

const port = args.options['port'] || 33080;
const deploy_dir = args.options['deploy-dir'] || '../deploy/dev';
const config = args.options['config'] || deploy_dir+'/conf/altair.ticketing.admin.ini';
const repos_dir = args.options['repos-dir'] || './var/venue-layout';
const backend_repos_dir = repos_dir + '/backend';
const frontend_repos_dir = repos_dir + '/frontend';
const report_to = args.options['report-to'];
if(report_to && !report_to.match(/@/)) {
	console.log('Invalid report-to: '+report_to);
	process.exit();
}
const report_from = args.options['report-from'] || report_to;
const sendmail = '/usr/sbin/sendmail -f{FROM} {TO}';

const fs = require('fs');
const loadConfig = (config) => {
	const ini = fs.readFileSync(config, 'utf8');
	var dict = { };
	ini.split(/\r?\n/).map(line => line.match(/^(\S+) = (.+)$/)).forEach(m => {
		if(m && dict[m[1]] === undefined) {
			dict[m[1]] = m[2];
		}
	});
	return dict;
};

const ejs = require('ejs');

const mysql_options = ((dict) => {
	const match = dict['sqlalchemy.url'].match(/\/\/([^:@]+):([^:@]+)@([^:@]+)(?::(\d+))?\/([^:@/\?]+)/);
	var options = {
		user: match[1],
		password: match[2],
		host: match[3],
		database: match[5]
	};
	if(match[4]) {
		options.port = match[4];
	}
	return options;
})(loadConfig(config));

const aws = require('aws-sdk');
const setupAWS = () => {
	const dict = loadConfig(config);
	aws.config.update({
	accessKeyId: dict['s3.access_key'],
		secretAccessKey: dict['s3.secret_key'],
		region: 'ap-northeast-1'
	});
	return aws;
};

const header_by_ext = (ext) => {
	const types = {
		html: 'text/html',
		js: 'text/javascript',
		json: 'application/json',
		meta: 'application/json',
		svg: 'image/svg+xml',
		svgz: [ 'gzip', 'image/svg+xml' ],
		xml: 'text/xml',
		css: 'text/css',
		gif: 'image/gif',
		png: 'image/png'
	};
	if((typeof types[ext]) == 'string') {
		return { 'Content-Type': types[ext] };
	}
	if((typeof types[ext]) == 'object' && types[ext][0]) {
		return {
			'Content-Encoding': types[ext][0],
			'Content-Type': types[ext][1]
		};
	}
	console.log('Unknown ext: '+ext);
	return { 'Content-Type': 'text/plain' };
};

const Busboy = require('busboy');
const { spawn } = require('child_process');
const zlib = require('zlib');
const mysql = require('mysql');

const send_report = (subject, content) => {
	if(!report_to || !report_from) {
		return new Promise((resolve, reject) => { resolve(); });
	}

	var sendmail_args = sendmail.replace(/{FROM}/, report_from).replace(/{TO}/, report_to).split(/ /);
	const cmd = sendmail_args.shift();

	return new Promise((resolve, reject) => {
		const mail = spawn(cmd, sendmail_args);
		if(!mail) {
			console.log('cannot spawn: '+sendmail_args.join(' '));
			reject('cannot spawn: '+sendmail_args.join(' '));
		}
		mail.stdin.write("From: "+report_from+"\r\n");
		mail.stdin.write("Subject: "+subject+"\r\n");
		mail.stdin.write("\r\n");
		mail.stdin.write(content.replace(/\n/g, "\r\n"));
		mail.stdin.end();
		mail.on('close', () => {
			resolve();
		});
	});
};

const query = (statement, params) => {
  return new Promise((resolve, reject) => {
		const connection = mysql.createConnection(mysql_options);
    connection.query(statement, params, (err, results) => {
			connection.end();
      if(err) {
        return reject(err);
      }
      resolve(results);
    });
 });
};

/*
const datetime_formatter = new Intl.DateTimeFormat([], {
	timeZone: 'Asia/Tokyo',
	year: 'numeric', month: '2-digit', day: '2-digit',
	hour: '2-digit', minute: '2-digit', second: '2-digit'
});
*/
const datetime_formatter = { format: (d) => {
	const p2 = (n) => {
		if(n < 10) {
			return '0' + n;
		} else {
			return '' + n;
		}
	};
	return d.getFullYear()+'-'+p2(1+d.getMonth())+'-'+p2(d.getDate())+' '+[d.getHours(), d.getMinutes(), d.getSeconds()].map(p2).join(':');
} };

const getUsernameFromHeader = (req) => {
	if(req.headers['authorization']) {
		const m = req.headers['authorization'].match(/^Basic (.+)$/);
		const auth = new Buffer(m[1], 'base64').toString();
		return (auth.split(':'))[0];
	}
	return null;
};

// TODO: promise reduceをutil化しておく

// FIXME: ns対応
const createBackendVenueParser = function(cb) {
	const saxStream = require("sax").createStream(/* strict= */true, { });
	var seat_count = 0;

	var stack = [ ];
	var object_stack = [ ];
	
	saxStream.on("opentag", function (node) {
		stack.push(node);
		if(node.name == 'si:object') {
			object_stack.push({ });
		}
	});
	saxStream.on("closetag", function (tagname) {
		if(stack[stack.length-1].name == 'si:object' && object_stack[object_stack.length-1]._class == 'Venue') {
			cb('venue.name', object_stack[object_stack.length-1].name);
		}
		if(stack[stack.length-1].name == 'si:object') {
			if(object_stack[object_stack.length-1]._class == 'Seat') {
				cb('seat.id', stack[stack.length-3].attributes['id']);
				seat_count++;
			}
		}
		if(stack[stack.length-1].name == 'si:object') {
			object_stack.pop();
		}
		stack.pop();
	});
	saxStream.on("text", function (text) {
		if(2 <= stack.length && stack[stack.length-2].name == 'si:object' && stack[stack.length-1].name == 'si:class') {
			object_stack[object_stack.length-1]._class = text;
		}
		if(2 <= stack.length && stack[stack.length-2].name == 'si:object' && stack[stack.length-1].name == 'si:property' && stack[stack.length-1].attributes['name'] == 'name') {
			object_stack[object_stack.length-1].name = text;
		}
	});
	saxStream.on("end", function() {
		cb('seat.count', seat_count);
	});
	return saxStream;
};

const createFrontendVenueParser = function(cb) {
	const saxStream = require("sax").createStream(/* strict= */true, { });

	var stack = [ ];
	
	saxStream.on("opentag", function (node) {
		const tag = node.name;
		if(!tag.match(/:/) && tag != 'svg' && tag != 'title' && tag != 'text') {
			if(node.attributes['id']) {
				cb('object.id', node.attributes['id']);
			}
		}
		stack.push(node);
	});
	saxStream.on("closetag", function (tagname) {
		stack.pop();
	});
	saxStream.on("text", function (text) {
	});
	saxStream.on("end", function() {
	});
	return saxStream;
};

const handleBackendList = (dir) => {
	const p = new Promise((resolve, reject) => {
		fs.readdir(dir, (err, files) => {
			if(err) {
				return reject(err);
			}
			var files = files.filter((name) => { return name.match(/\.xml$/); });
			Promise.all(files.map(file => {
				return new Promise((resolve, reject) => {
					fs.stat(dir+'/'+file, (err, stats) => {
						if(err) {
							return resolve();
						}
						fs.readFile(dir+'/'+file+'.meta', { encoding: 'utf-8' }, (err, data) => {
						  try {
								resolve({
									filename: file,
									size: stats.size,
									mtime: datetime_formatter.format(stats.mtime),
									content: JSON.parse(data)
								});
							} catch(ex) {
								resolve({ });
							}
						});
					});
				});
			})).then(parsed_list => {
				resolve(parsed_list.filter(parsed => { return parsed && parsed.filename; }));
			});
		});
	});
	return {
		pipe: (res) => {
			p.then((resolved) => {
				// newer first
				resolved.sort((a, b) => {
					if(a.mtime < b.mtime) { return +1; }
					if(b.mtime < a.mtime) { return -1; }
					return 0;
				});
				res.write(JSON.stringify(resolved));
				res.end();
			});
		}
	};
};

const handleFrontendList = (dir) => {
	const p = new Promise((resolve, reject) => {
		fs.readdir(dir, (err, files) => {
			if(err) {
				return reject(err);
			}
			Promise.all(files.map(subdir => {
				return new Promise((resolve, reject) => {
					fs.stat(dir+'/'+subdir, (err, stats) => {
						if(!stats.isDirectory()) {
							resolve();
							return;
						}
						fs.readdir(dir+'/'+subdir, (err, files) => {
							var meta = files.filter((name) => { return name.match(/\.meta$/); });
							if(meta.length == 0) {
								resolve();
								return;
							}
							fs.readFile(dir+'/'+subdir+'/'+meta[0], { encoding: 'utf-8' }, (err, data) => {
								try {
									resolve({
										filename: subdir+'/'+meta[0].replace(/\.meta$/, ''),
										size: stats.size,
										mtime: datetime_formatter.format(stats.mtime),
										content: JSON.parse(data)
									});
								} catch(ex) {
									resolve({ });
								}
							});
						});
					});
				});
			})).then(parsed_list => {
				resolve(parsed_list.filter(parsed => { return parsed && parsed.filename; }));
			});
		});
	});
	return {
		pipe: (res) => {
			p.then((resolved) => {
				// newer first
				resolved.sort((a, b) => {
					if(a.mtime < b.mtime) { return +1; }
					if(b.mtime < a.mtime) { return -1; }
					return 0;
				});
				res.write(JSON.stringify(resolved));
				res.end();
			});
		}
	};
};

const generateDirectoryName = () => {
  return (((new Date()).getTime()/1000).toString(16).replace(/\./, '')+'00000000').substr(0, 13); // php uniqid() compatible
	// return Math.random().toString(16).slice(2);
};

const handleUploadRequest = (req, res) => {
	var jobs = [ ];
	var busboy = new Busboy({ headers: req.headers });
	var back_base;
	var back_name;
	var front_name;
	var front_base;
	var front_meta;
	var front_files = [ ];

	busboy.on('file', function(fieldname, file, filename, encoding, mimetype) {
		if(fieldname == 'back' && filename !== '') {
			// XMLを書き出す
			back_base = generateDirectoryName();
			const basename = filename.replace(/\.[^\.]+$/, '');
			if(basename.match(/^[0-9a-z\.-]+$/)) {
				back_base += "."+basename;
			}
			var back_meta = {
				name: "",
				seat_count: 0,
				uploaded_by: getUsernameFromHeader(req) || process.env['AUTH_USER'] || "?"
			};

			jobs.push(new Promise((resolve, reject) => {
				const venueParser = createBackendVenueParser((key, value) => {
					if(key == 'venue.name') {
						back_meta.name = value;
					} else if(key == 'seat.count') {
						back_meta.seat_count = value;
					}
				});

				const fileWriter = fs.createWriteStream(backend_repos_dir+'/'+back_base+'.xml', { flags : 'w' });
				fileWriter.on('close', function() {
					// XML書き出し完了

					// metaを書き出す
					fs.writeFile(backend_repos_dir+'/'+back_base+'.xml.meta', JSON.stringify(back_meta), (err) => {
						if(err) {
							reject(err);
						}
						resolve();
					});
				});

				file
				.pipe(venueParser)
				.pipe(fileWriter);
			}));
		} else if(fieldname == 'front[]' && filename != '') {
			if(filename.match(/\.svg$/)) {
				if(!front_base) {
					front_base = generateDirectoryName();
					fs.mkdirSync(frontend_repos_dir+'/'+front_base);
				}
				// TODO: check filename safety and tail .svg

				const path = frontend_repos_dir+'/'+front_base+'/'+filename;
				const svgz_path = path.replace(/\.svg$/, '')+'.svgz';

				jobs.push(new Promise((resolve, reject) => {
					// FIXME: 関数名を見直す
					const venueParser = createBackendVenueParser((key, value) => {
						if(key == 'venue.name') {
							if(front_name == null) {
								front_name = value;
							}
						}
					});

					const fileWriter = fs.createWriteStream(path, { flags : 'w' });
					fileWriter.on('close', function() {
						front_files.push(filename);

						const xsltproc = spawn('xsltproc', [ 'strip-metadata.xsl', path ]);
						const svgzFileWriter = fs.createWriteStream(svgz_path, { flags : 'w' });
						xsltproc.stdout
						.pipe(zlib.createGzip())
						.pipe(svgzFileWriter);
						xsltproc.on('close', (code) => {
						  console.log('xsltproc terminated by '+code);
							resolve();
						});
					});

					file
					.pipe(venueParser)
					.pipe(fileWriter);
				}));
			} else if(filename.match(/\.json$/)) {
				jobs.push(new Promise((resolve, reject) => {
					// JSON読み込み
					if(front_meta) {
						// TODO: jsonが2つあったらエラー
					}
					var buf = "";
					file.on('data', function(data) {
						buf += data;
					});
					file.on('end', function() {
						// JSON読み込み完了
						front_meta = JSON.parse(buf);
						resolve();
					});
				}));
			}
		} else {
			file.on('data', function(data) { });
			file.on('end', function() { });
		}
	});
	busboy.on('finish', function() {
		if(jobs.length == 0) {
			res.writeHead(400, { Connection: 'close', 'Content-Type': 'text/plain' });
			res.write("No files were uploaded.");
			res.end();
			return;
		}
		Promise.all(jobs)
		.then(() => {
			if(front_base) {
				if(!front_meta && front_files.length == 1) {
					var pages = { };
					pages[front_files[0]] = { name: "全体図", root: true };
					front_meta = { pages: pages };
				}
				if(!front_meta) {
					// TODO: エラー
					return;
				}

				// metadata.raw.json書き出し
				const p1 = new Promise((resolve, reject) => {
					fs.writeFile(frontend_repos_dir+'/'+front_base+'/metadata.raw.json', JSON.stringify(front_meta), (err) => {
						if(err) { reject(err); } else { resolve(); }
					});
				});

				// metadata.json書き出し
				const p2 = new Promise((resolve, reject) => {
					var pages = { };
					Object.keys(front_meta.pages).forEach(name => {
						pages[name.replace(/\.svg$/, '.svgz')] = front_meta.pages[name];
					});
					var meta = { pages: pages };
					fs.writeFile(frontend_repos_dir+'/'+front_base+'/metadata.json', JSON.stringify(meta), (err) => {
						if(err) { reject(err); } else { resolve(); }
					});
				});

				// metadata.json.meta書き出し
				const p3 = new Promise((resolve, reject) => {
				  const json_meta = {
					  name: front_name || "?",
					uploaded_by: getUsernameFromHeader(req) ||   process.env['AUTH_USER'] || "?"
					};
				  fs.writeFile(frontend_repos_dir+'/'+front_base+'/metadata.json.meta', JSON.stringify(json_meta), (err) => {
					  if(err) { reject(err); } else { resolve(); }
					});
				});

				return new Promise((resolve, reject) => {
					Promise.all([ p1, p2, p3 ]).then(() => {
						resolve();
					}, (err) => {
						reject(err);
					});
				});
			} else {
				return true;
			}
		})
		.then(() => {
			if(back_base) {
				// リダイレクトする for backend
				res.writeHead(303, { Connection: 'close', Location: 'checker.html#/venue-admin/upload/backend/'+back_base+'.xml' });
			} else if(front_base) {
				// リダイレクトする for frontend
				res.writeHead(303, { Connection: 'close', Location: 'viewer.html#/venue-admin/upload/frontend/'+front_base+'/metadata.json' });
			} else {
				res.writeHead(500, { Connection: 'close', 'Content-Type': 'text/plain' });
				res.write("unexpected");
			}
			res.end();
		}, (err) => {
			res.writeHead(500, { Connection: 'close', 'Content-Type': 'text/plain' });
			res.write(err);
			res.end();
		});
	});
	req.pipe(busboy);
};

const getSite = (dirname) => {
	return query('SELECT Site.id as site_id, Venue.id as venue_id FROM Site LEFT JOIN Venue ON Venue.site_id=Site.id and Venue.deleted_at is null WHERE (drawing_url like concat("%/svgs/", ?, ".xml") OR backend_metadata_url like concat("%/backend/", ?, "/metadata.json")) and Site.deleted_at is null', [ dirname, dirname ]);
};

const getSiteInfo = (id) => {
  return query('SELECT Site.id as site_id, Site.name as site_name, Venue.sub_name as sub_name, Site.metadata_url, Site.backend_metadata_url, Venue.id as venue_id FROM Site LEFT JOIN Venue ON Venue.site_id=Site.id and Venue.deleted_at is null WHERE Site.id=?', [ id ])
	.then((results) => { return new Promise((resolve, reject) => {
		if(results.length == 0) {
			return reject();
		}
    var info = {
      site: {
        id: results[0].site_id,
        name: results[0].site_name,
        metadata_url: results[0].metadata_url,
        backend_metadata_url: results[0].backend_metadata_url
      },
      sub_name: results[0].sub_name,
      venues: [ ]
    };
    resolve(info);
  }); })
  .then((info) => {
    return query('SELECT Venue.id venue_id, Venue.created_at created_at, Performance.name, Performance.id performance_id, Performance.start_on, Event.id event_id FROM Venue LEFT JOIN Performance ON Venue.performance_id=Performance.id AND Performance.deleted_at IS NULL LEFT JOIN Event ON Performance.event_id=Event.id AND Event.deleted_at IS NULL WHERE Venue.site_id=?', [ id ])
    .then((results) => {
      info.venues = results.map((r) => { return { id: r.venue_id, performance: r.performance_id ? {
        id: r.performance_id,
        name: r.name,
        start_on: datetime_formatter.format(r.start_on),
        event: { id: r.event_id }
      } : null, created_at: datetime_formatter.format(r.created_at) }; });
      return info;
    });
  })
  .then((info) => {
    return query('SELECT COUNT(L0Seat.l0_id) as c FROM L0Seat WHERE site_id=?', [ id ])
    .then((results) => {
      for(var i=0 ; i<info.venues.length ; i++) {
        info.venues[0].seat_count = results[0].c;
      }
      return info;
    });
  })
  ;
};

const updateSite = (site_id, prefecture, subname) => {
	return query('UPDATE Site,Venue SET Site.prefecture=?, Venue.sub_name=? WHERE Site.id=? and Site.id=Venue.site_id and Site.deleted_at is null and Venue.deleted_at is null', [ prefecture, subname, site_id ]);
};

const getBackendPath = (url) => {
  if(url) {
  	return backend_repos_dir + '/' + url.replace(/^.+\/([^\/]+)$/, '$1');
  }
};

const getFrontendPath = (url) => {
  if(url) {
  	return frontend_repos_dir + '/' + url.replace(/^.+\/([^\/]+\/[^\/]+\.json)$/, '$1');
  }
};

const handleReplaceRequest = (param, res) => {
	res.writeHead(200, { Connection: 'close', 'Content-Type': 'text/plain' });
	const basename = function(path) {
		return path.replace(/^.+\/([^\/]+)$/, '$1');
	};
	const svg = getFrontendPath(param['frontend']);
  const args = [
		'-s', param['site_id'],
		'-U', param['frontend_dirname'],
		config, svg ];
	try {
		fs.statSync(svg);
	} catch(err) {
		res.writeHead(400, { 'Content-Type': 'text/plain' });
		res.write('frontend svg is not found.');
		res.end();
		return;
	}
	const frontend_venue_import = spawn(deploy_dir+'/bin/frontend_venue_import', args);
	
	res.write("exec: frontend_venue_import " + args.join(' ') + "\n");
	console.log("exec: frontend_venue_import " + args.join(' ') + "\n");
	frontend_venue_import.stdout
	.on('data', (data) => {
		console.log("[out] "+data);
		res.write(data);
	});
	frontend_venue_import.stderr
	.on('data', (data) => {
		console.log("[err] "+data);
		res.write(data);
	});
	frontend_venue_import
	.on('close', (code) => {
	  console.log('frontend_venue_import terminated by '+code);
		res.write('complete');
		res.end();
	});
};

const handleRegisterRequest = (param, res) => {
	const basename = function(path) {
		return path.replace(/^.+\/([^\/]+)$/, '$1');
	};
	const svg = getBackendPath(param['backend']);
	try {
		fs.statSync(svg);
	} catch(err) {
		res.writeHead(400, { 'Content-Type': 'text/plain' });
		res.write('backend svg is not found.');
		res.end();
		return;
	}
	var backend_dirname = basename(param['backend']).replace(/^[0-9a-f]+\.(.+)\.[^\.]+$/, '$1');
	if(param['backend_dirname']) {
		backend_dirname = param['backend_dirname'];
	}
	const to_hex = function(str) {
		return encodeURI(str).replace(/%/g, '');
	};
	if(!param['organization']) {
		res.writeHead(400, { 'Content-Type': 'text/plain' });
		res.write('organization is required.');
		res.end();
		return;
	}
	const hex_prefecture = to_hex(param['prefecture']);

	if(param['frontend']) {
		const svg_frontend = getFrontendPath(param['frontend']);
		try {
			fs.statSync(svg_frontend);
		} catch(err) {
			res.writeHead(400, { 'Content-Type': 'text/plain' });
			res.write('frontend svg is not found.');
			res.end();
			return;
		}
	}

	var args = [ '-v', /* dry run '-n', */
		'-A', '10',
		'-O', param['organization'],
		'-U', backend_dirname
	];
	if(hex_prefecture) {
		args = args.concat([ '-P', hex_prefecture ]);
	} else {
		args = args.concat([ '-P', '""' ]);
	}
	args = args.concat([ config, svg ]);
	
	if(!backend_dirname) {
		res.writeHead(400, { 'Content-Type': 'text/plain' });
		res.write('backend dirname is required.');
		res.end();
		return;
	}
	getSite(backend_dirname)
	.then((r) => {
		if(r.length == 0) {
			// ok
			console.log("exec: venue_import " + args.join(' '));
			const venue_import = spawn(deploy_dir+'/bin/venue_import', args, { env: { LC_ALL: 'ja_JP.utf8' } });
			res.writeHead(200, { Connection: 'close', 'Content-Type': 'text/plain' });
			res.write("exec: venue_import " + args.join(' ') + "\n");
			var cleanup = function() { };
			var timer = setTimeout(function() {
				timer = null;
				res.write('venue_import seems to running in 10 sec, going background.');
				res._background = true;
				res.end();
				connections[res._connection_id] = 'venue_import '+backend_dirname;
				cleanup = () => {
					console.log('Cleaning up for '+res._connection_id);
					if(res._connection_id !== undefined) {
						delete connections[res._connection_id];
					}
				};
			}, 10*1000);
			var buf = [ ];
			venue_import.stdout
			.on('data', (data) => {
				console.log("[out] "+data);
				buf.push(data);
			});
			venue_import.stderr
			.on('data', (data) => {
				console.log("[err] "+data);
				buf.push(data);
			});
			venue_import
			.on('close', (code) => {
				if(timer) {
					clearTimeout(timer);
					res.write('venue_import terminated by '+code+' (maybe too early)'+"\n");
					res.write(buf.join("\n"));
					res.end();
				}
			  console.log('venue_import terminated by '+code);
				
				// site infoをupdateする
				getSite(backend_dirname)
				.then((r) => {
					if(r.length == 1) {
						const site_id = r[0].site_id;
						const venue_id = r[0].venue_id;
						buf = ["See https://service.ticketstar.jp/venues/show/"+venue_id,
						 "Registered successfully as site="+site_id,
						 ""].concat(buf)
						updateSite(site_id, param['prefecture'], param['sub_name'])
						.then(() => {
							// complete
							
							registerFrontend(param, site_id)
							.then(() => {
								// complete
								if(cleanup) {
									cleanup();
								}
								send_report('result of venue-import [v2]', buf.map(l => l+"\r\n").join(''));
							});
						});
					} else {
						// maybe failed
						if(cleanup) {
							cleanup();
						}
						buf = ["venue_import failed.", ""].concat(buf);
						send_report('result of venue-import [ERROR] [v2]', buf.map(l => l+"\r\n").join(''));
					}
				})
			});
		} else {
			// found
			res.write('already registered: id='+r[0].site_id+', venue.id='+r[0].venue_id);
			res.end();
		}
	});
};

const registerFrontend = (param, site_id) => {
	return new Promise((resolve, reject) => {
		if(!param['frontend']) {
			// エラーにしない
			resolve();
			return;
		}
		
		var frontend_dirname = param['frontend'].replace(/^.+\/([^\/]+)\/[^\/]+$/, '$1');
		const svg = getFrontendPath(param['frontend']);
		if(param['frontend_dirname']) {
			frontend_dirname = param['frontend_dirname'];
		}
		const args = [
			'-s', site_id,
			'-U', frontend_dirname,
			config, svg ];

		const frontend_venue_import = spawn(deploy_dir+'/bin/frontend_venue_import', args);
		
		console.log("exec: frontend_venue_import " + args.join(' ') + "\n");
		frontend_venue_import.stdout
		.on('data', (data) => {
			console.log("[out] "+data);
		});
		frontend_venue_import.stderr
		.on('data', (data) => {
			console.log("[err] "+data);
		});
		frontend_venue_import
		.on('close', (code) => {
		  console.log('frontend_venue_import terminated by '+code);
			resolve();
		});
	});
};

const handleCheckRequest = (param, res) => {
	if(!param['frontend']) {
		res.writeHead(400, { 'Content-Type': 'text/plain' });
		res.write('frontend is required.');
		res.end();
		return;
	}
	const frontend_json = getFrontendPath(param['frontend']);

	var in_backend = { };
	const backendVenueParser = createBackendVenueParser((key, value) => {
		if(key == 'seat.count') {
			res.write('found '+value+' seats in backend'+"\n");
		}
		if(key == 'seat.id') {
			in_backend[value] = '';
		}
	});

	var in_frontend = [ ];
	const frontendHandler = (key, value) => {
		if(key == 'object.id') {
		  in_frontend[value] = true;
		}
	};

	const analyze = (res) => {
		res.write('found '+Object.keys(in_frontend).length+' objects in frontend'+"\n");
		var covered = 0;
		for(var id in in_frontend) {
			if(in_backend[id] === '') {
				in_backend[id] = true;
				covered++;
			} else if(in_backend[id] === true) {
				// frontendに2回以上現れている
			}
		}
		const total = Object.keys(in_backend).length;
		res.write("Coverage: "+(covered/total*100)+"% ("+covered+"/"+total+")\n");
		for(var id in in_backend) {
			if(in_backend[id] === '') {
				// frontendに一度も出てこない
				res.write("[WARN] id="+id+" is not found in frontend\n");
			}
		}
		res.end();
	};

	const backendStream = (param) => {
		return new Promise((resolve, reject) => {
			if(param['backend']) {
				resolve(fs.createReadStream(getBackendPath(param['backend'])));
			} else {
			  const match = param['backend_meta'].match(/^s3:\/\/([^\/]+)\/(.+)$/);
				if(match) {
					const aws = setupAWS();
					const s3 = new aws.S3();
					s3.getObject({ Bucket: match[1], Key: match[2] }, (err, data) => {
						if(err) {
							// TODO:
							return;
						}
						const parsed = JSON.parse(data.Body.toString('utf-8'));
						for(var k in parsed.pages) {
							const key = match[2].replace(/\/[^\/]+$/, '/'+k);
							resolve(s3.getObject({ Bucket: match[1], Key: key }).createReadStream());
							return;
						}
					});
				} else {
					// unexpected
					reject(param['backend_meta']);
				}
			}
		});
	};
	backendStream(param)
	.then((streamB) => {
		streamB.pipe(backendVenueParser);
		streamB.on('end', () => {
			fs.readFile(frontend_json, { encoding: 'utf-8' }, (err, data) => {
				const meta = JSON.parse(data);
				var svgs = Object.keys(meta.pages).map(name => {
					return frontend_json.replace(/\/[^\/]+$/, '/')+name;
				});
				const task = svgs.map(svg => (prev) => { return new Promise((resolve, reject) => {
					const frontendVenueParser = createFrontendVenueParser(frontendHandler);
					const gunzip = zlib.createGunzip();
					frontendVenueParser.on('end', () => {
						resolve("parse-"+svg);
					});
					fs.createReadStream(svg).pipe(gunzip).pipe(frontendVenueParser);
				}); });
		
				task.reduce((ret, p) => {
					return ret.then(p);
				}, new Promise((resolve, reject) => { resolve("dummy"); }))
				.then((prev) => {
					// complete both
					analyze(res);
				});
			});
		});
	});
};

const handlePostRequest = (param, req, res) => {
	if(param['check']) {
    if(param['site_id']) {
			// 既存サイトについてのcheck
			getSiteInfo(param['site_id'])
			.then((info) => {
				handleCheckRequest({
					backend_meta: info.site.backend_metadata_url,
					frontend: param['frontend']
				}, res);
		   }, (error) => {
				res.write('No such site: '+site_id);
				res.end();
			});
			return;
		} else {
			// SVG 2つ使ってのcheck
			return handleCheckRequest(param, res);
		}
	} else if(param['register']) {
		return handleRegisterRequest(param, res);
	} else if(param['replace']) {
		return handleReplaceRequest(param, res);
	} else {
		res.writeHead(404, { 'Content-Type': 'text/plain' });
		res.end();
	}
};

var counter = 0;
var connections = { };
const listener = (req, res) => {
	const operator = getUsernameFromHeader(req);
	
	const count = (++counter) % 1000;
	const prefix = ('000' + count).substr(-4);
	console.log(prefix + ' ' + req.method + ' ' + req.url + (operator ? ' by '+operator : ''));

	const connection_id = (new Date()).getTime() + " " +counter;
	connections[connection_id] = [ new Date(), req.url + (operator ? ' by '+operator : '') ];

  const path = req.url.replace(/\?.*$/, '');
	var param = { };
	const query_string = req.url.match(/^.+\?(.*)$/);
	if(query_string) {
		query_string[1].split(/&/).forEach(kv => {
			((k, v) => { param[k] = decodeURIComponent(v); }).apply(null, kv.split(/=/))
	  });
	}

	res.writeHead = ((self, orig) => { return (code, headers) => {
		console.log(prefix + " -> " + code);
		return orig.call(self, code, headers);
	}; })(res, res.writeHead);

	res._connection_id = connection_id;
	res.end = ((self, orig) => { return () => {
		if(self._background === undefined) {
			delete connections[connection_id];
		}
		return orig.call(self);
	}; })(res, res.end);
	
	if(req.method == 'POST') {
		if(path.indexOf('/venue-admin/upload/') == 0) {
			return handleUploadRequest(req, res);
		} else if(path.indexOf('/venue-admin/deploy/') == 0) {
			const querystring = require('querystring');
			var data = '';
			req.on('readable', function(chunk) {
				var chunk = req.read();
				if(chunk != null) {
					data += chunk;
				}
			});
			req.on('end', function() {
				const param = querystring.parse(data);
				console.log(prefix + ' ' + data);
				handlePostRequest(param, req, res);
			});
			return;
		}

		console.log("-> not found");
		res.writeHead(404, { 'Content-Type': 'text/plain' });
		res.write('Not Found!');
		res.end();
		return;
	}

	// handle as GET
	var match;
	if(path == '/venue-admin/ps') {
		res.writeHead(200, { 'Content-Type': 'text/plain', 'Refresh': '5' });
		const now = new Date().getTime();
		Object.keys(connections).forEach((c) => {
			if(c != connection_id) {
				const name = connections[c];
				const params = c.split(/ /);
				res.write(name + " (" + Math.floor(((now - parseInt(params[0])))/1000) + "sec)\n");
			}
		});
		res.end();
		return;
	} else if(match = path.match(/^\/(venue-admin\/([a-z]+\/)*[0-9a-z\._-]+\.(html|js|css|png))$/)) {
		const local_path = 'htdocs/'+match[1];
		try {
			fs.statSync(local_path);
			res.writeHead(200, header_by_ext(match[3]));
			if(path.match(/^\/venue-admin\/upload\/js\/carts\.js$/)) {
				// remove /cart/static/img/settlement/
				fs.readFile(local_path, { encoding: 'utf-8' }, (err, data) => {
					res.write("// auto hacked version for venue-admin\n");
					res.write(data.replace('/cart/static/img/settlement/', ''));
					res.end();
				});
			} else {
				fs.createReadStream(local_path).pipe(res);
			}
			return;
		} catch(ex) {
			// 404
			console.log(ex);
		}
	} else if(match = path.match(/^\/venue-admin\/upload\/((?:backend|frontend)\/(?:(?:[0-9a-z]+\/)?(?:[0-9a-z]+\.)?[0-9a-zA-Z_-]+\.([a-z]+)(\.meta)?))$/)) {
		const local_path = repos_dir + '/' + match[1];
		try {
			fs.statSync(local_path);
			res.writeHead(200, header_by_ext(match[2]));
			fs.createReadStream(local_path).pipe(res);
			return;
		} catch(ex) {
			// 404
			console.log(ex);
    }
	} else if(match = path.match(/^\/venue-admin\/deploy\/((?:backend|frontend)\/(?:(?:[0-9a-z]+\/)?(?:[0-9a-z]+\.)?[0-9a-zA-Z_-]+\.([a-z]+)(\.meta)?))$/)) {
		const local_path = repos_dir + '/' + match[1];
		try {
			fs.statSync(local_path);
			res.writeHead(200, header_by_ext(match[2]));
			fs.createReadStream(local_path).pipe(res);
			return;
		} catch(ex) {
			// 404
			console.log(ex);
		}
	} else if(match = path.match(/^\/venue-admin\/deploy\/run\.php/)) {
		res.writeHead(200, { 'Content-Type': 'text/html; charset=UTF-8' });
		res.write('<script>location.href = "./run.html";</script>');
		res.end();
		return;
	} else if(match = path.match(/^\/venue-admin\/deploy\/run$/)) {
		const site_id = param.site * 1;
		if(!site_id) {
			res.writeHead(404);
			res.end();
			return;
		}
		const local_path = 'htdocs/venue-admin/deploy/template/run.html';
		res.writeHead(200, { 'Content-Type': 'text/html; charset=UTF-8' });
		getSiteInfo(site_id)
		.then((info) => {
  		var opt = { };
      info.dirname = (getFrontendPath(info.site.metadata_url) || "").replace(/^.+\/([^\/]+)\/[^\/]+$/, '$1');
  		res.write(ejs.compile(fs.readFileSync(local_path, 'utf8'), opt)(info));
      res.end();
    }, (error) => {
			res.write('No such site: '+site_id);
			res.end();
		});
    return;
	} else if(match = path.match(/^\/venue-admin\/deploy\/site$/)) {
		const id = param.id * 1;
		if(!id) {
			res.writeHead(404);
			res.end();
			return;
		}
		const local_path = 'htdocs/venue-admin/deploy/template/site.html';
		res.writeHead(200, { 'Content-Type': 'text/html; charset=UTF-8' });
		getSiteInfo(id)
		.then((info) => {
			var opt = { };
			try {
				info.svgs = [ { filename: "?", name: "?" } ];
				info.host = "localhost";
				res.write(ejs.compile(fs.readFileSync(local_path, 'utf8'), opt)(info));
			} catch(ex) {
				res.write(ex.toString());
			}
			res.end();
		});
		return;
	} else if(match = path.match(/^\/venue-admin\/api\/backend$/)) {
		res.writeHead(200, { 'Content-Type': 'application/json' });
		handleBackendList(backend_repos_dir).pipe(res);
		return;
	} else if(match = path.match(/^\/venue-admin\/api\/frontend$/)) {
		res.writeHead(200, { 'Content-Type': 'application/json' });
		handleFrontendList(frontend_repos_dir).pipe(res);
		return;
	} else if(match = path.match(/^\/venue-admin\/api\/organization$/)) {
		query('SELECT ?? FROM Organization', [['id', 'code', 'name']])
		.then((results) => {
			res.writeHead(200, { 'Content-Type': 'application/json' });
			res.write(JSON.stringify(results));
			res.end();
		}, (err) => {
			res.writeHead(500, { 'Content-Type': 'text/plain' });
			res.write(err);
			res.end();
		});
		return;
	} else if(match = path.match(/^\/venue-admin\/api\/venue$/)) {
		query('SELECT o.name organization, s.id, v.id venue,s.name,v.sub_name,metadata_url,DATE_FORMAT(CONVERT_TZ(s.created_at, "+00:00", "+09:00"),GET_FORMAT(DATETIME,"JIS")) created_at FROM Site s INNER JOIN Venue v ON v.site_id=s.id AND v.performance_id is null AND v.deleted_at is null INNER JOIN Organization o ON o.id=v.organization_id WHERE s.deleted_at is null AND NOT (IFNULL(s.backend_metadata_url, s.drawing_url) LIKE "dummy/%") ORDER BY s.name', [[ ]])
		.then((results) => {
			res.writeHead(200, { 'Content-Type': 'application/json' });
			res.write(JSON.stringify(results));
			res.end();
		}, (err) => {
			res.writeHead(500, { 'Content-Type': 'text/plain' });
			res.write(err);
			res.end();
		});
		return;
	} else if(match = path.match(/^\/venue-admin\/upload\/frontend\.php\/([0-9a-f]+)\/metadata\.json$/)) {
		const base = match[1];
		res.writeHead(200, { 'Content-Type': 'application/json' });
		fs.readFile(frontend_repos_dir+'/'+base+'/metadata.json', { encoding: 'utf-8' }, (err, data) => {
			const meta = JSON.parse(data);
			if(param.mode == 'seat_types') {
				var parts = { };
				for(var p in meta.pages) {
					parts[p] = '/venue-admin/upload/frontend/' + base + '/' + p;
				}
				const replace = {
					BASE: '/venue-admin/upload',
					DIR: base,
					FILE: 'metadata.json',
					VENUE: param.name,
					PARTS: JSON.stringify(parts)
				};
				fs.readFile('htdocs/venue-admin/upload/template/seat_types.json.template', { encoding: 'utf-8' }, (err, data) => {
					res.write(data.replace(/\${([A-Z]+)}/g, (_, tag) => {
						return replace[tag];
					}));
					res.end();
				});
			} else {
				fs.readFile('htdocs/venue-admin/upload/template/seats.json.template', { encoding: 'utf-8' }, (err, data) => {
					res.write(data.replace(/"pages": { }/, '"pages": '+JSON.stringify(meta.pages)));
					res.end();
				});
			}
		});
		return;
	}
	
	console.log("-> not found");
	res.writeHead(404, { 'Content-Type': 'text/plain' });
	res.write('Not Found!');
	res.end();
};

console.log('Listening on :'+port);
require('http').createServer(listener)
.listen(port, '0.0.0.0');
