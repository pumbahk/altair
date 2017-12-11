const port = 40080;

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

const fs = require('fs');
const Busboy = require('busboy');
const { spawn } = require('child_process');
const zlib = require('zlib');

const datetime_formatter = new Intl.DateTimeFormat([], {
	timeZone: 'Asia/Tokyo',
	year: 'numeric', month: 'numeric', day: 'numeric',
	hour: 'numeric', minute: 'numeric', second: 'numeric'
});

// FIXME: タグの登場順が変わるとうまく動かない問題...
const createVenueParser = function(cb) {
	const saxStream = require("sax").createStream(/* strict= */true, { });
	var seat_count = 0;

	var current_tag;
	var current_object;
	saxStream.on("opentag", function (node) {
	  current_tag = node.name;
		if(current_object == 'venue' && node.name == 'si:property' && node.attributes && node.attributes.name == 'name') {
			current_object = 'venue.name';
		}
	});
	saxStream.on("closetag", function (tagname) {
		current_tag = null;
	});
	saxStream.on("text", function (text) {
	  if(current_tag == 'title') {
			cb('title', text);
	  } else if(current_tag == 'si:class') {
			if(text == 'Seat') {
				current_object = null;
				seat_count++;
			} else if(text == 'Venue') {
				current_object = 'venue';
			} else {
				current_object = null;
			}
	  } else if(current_tag == 'si:property') {
			if(current_object == 'venue.name') {
				cb('venue.name', text);
			}
		}
	});
	saxStream.on("end", function() {
		cb('seat.count', seat_count);
	});
	return saxStream;
};

const handleBackendList = (dir) => {
	const p = new Promise((resolve, reject) => {
		fs.readdir(dir, (err, files) => {
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
				res.write(JSON.stringify(resolved));
				res.end();
			});
		}
	};
};

const handleFrontendList = (dir) => {
	const p = new Promise((resolve, reject) => {
		fs.readdir(dir, (err, files) => {
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
								resolve({
									filename: subdir+'/'+meta[0].replace(/\.meta$/, ''),
									size: stats.size,
									mtime: datetime_formatter.format(stats.mtime),
									content: JSON.parse(data)
								});
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
				res.write(JSON.stringify(resolved));
				res.end();
			});
		}
	};
};

const generateDirectoryName = () => {
	// TODO: PHPのような時系列で並ぶIDを生成したい
	return Math.random().toString(16).slice(2);
};

const handlePostRequest = (req, res) => {
	var jobs = [ ];
	var busboy = new Busboy({ headers: req.headers });
	var back_base;
	var back_name;
	var front_name;
	var front_base;
	var front_meta;
	var front_files = [ ];

	busboy.on('file', function(fieldname, file, filename, encoding, mimetype) {
		if(fieldname == 'back') {
			// XMLを書き出す
			back_base = generateDirectoryName();
			const basename = filename.replace(/\.[^\.]+$/, '');
			if(basename.match(/^[0-9a-z\.-]+$/)) {
				back_base += "."+basename;
			}
			var back_meta = {
				name: "",
				seat_count: 0,
				uploaded_by: process.env['AUTH_USER'] || "?"
			};

			jobs.push(new Promise((resolve, reject) => {
				const venueParser = createVenueParser((key, value) => {
					if(key == 'title') {
						back_meta.name = value;
					} else if(key == 'seat.count') {
						back_meta.seat_count = value;
					}
				});

				const fileWriter = fs.createWriteStream('var/venue-layout/backend/'+back_base+'.xml', { flags : 'w' });
				fileWriter.on('close', function() {
					// XML書き出し完了

					// metaを書き出す
					fs.writeFile('var/venue-layout/backend/'+back_base+'.meta', JSON.stringify(back_meta), (err) => {
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
		} else if(fieldname == 'front[]') {
			if(filename.match(/\.svg$/)) {
				if(!front_base) {
					front_base = generateDirectoryName();
					fs.mkdirSync('var/venue-layout/frontend/'+front_base);
				}
				// TODO: check filename safety and tail .svg

				const path = 'var/venue-layout/frontend/'+front_base+'/'+filename;
				const svgz_path = path.replace(/\.svg$/, '')+'.svgz';

				jobs.push(new Promise((resolve, reject) => {
					const venueParser = createVenueParser((key, value) => {
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
		}
	});
	busboy.on('finish', function() {
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
					fs.writeFile('var/venue-layout/frontend/'+front_base+'/metadata.raw.json', JSON.stringify(front_meta), (err) => {
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
					fs.writeFile('var/venue-layout/frontend/'+front_base+'/metadata.json', JSON.stringify(meta), (err) => {
						if(err) { reject(err); } else { resolve(); }
					});
				});

				// metadata.json.meta書き出し
				const p3 = new Promise((resolve, reject) => {
				  const json_meta = {
					  name: front_name || "?",
						uploaded_by: process.env['AUTH_USER'] || "?"
					};
				  fs.writeFile('var/venue-layout/frontend/'+front_base+'/metadata.json.meta', JSON.stringify(json_meta), (err) => {
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

const listener = (req, res) => {
	const path = req.url;
	
	console.log(req.method + ' ' + path);
	
	if(req.method == 'POST') {
		handlePostRequest(req, res);
		return;
	}

	// handle as GET
	var match;
	if(match = path.match(/^\/(venue-admin\/([a-z]+\/)*[0-9a-z\._-]+\.(html|js|css|png))$/)) {
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
	} else if(match = path.match(/^\/venue-admin\/upload\/((?:backend|frontend)\/(?:(?:[0-9a-z]+\/)?(?:[0-9a-z]+\.)?[0-9a-z_-]+\.([a-z]+)(\.meta)?))$/)) {
		const local_path = 'var/venue-layout/'+match[1];
		try {
			fs.statSync(local_path);
			res.writeHead(200, header_by_ext(match[2]));
			fs.createReadStream(local_path).pipe(res);
			return;
		} catch(ex) {
			// 404
			console.log(ex);
		}
	} else if(match = path.match(/^\/venue-admin\/api\/backend$/)) {
		res.writeHead(200, { 'Content-Type': 'application/json' });
		handleBackendList('var/venue-layout/backend').pipe(res);
		return;
	} else if(match = path.match(/^\/venue-admin\/api\/frontend$/)) {
		res.writeHead(200, { 'Content-Type': 'application/json' });
		handleFrontendList('var/venue-layout/frontend').pipe(res);
		return;
	} else if(match = path.match(/^\/venue-admin\/upload\/frontend\.php\/([0-9a-f]+)\/metadata\.json(?:\?(.+))?$/)) {
		const base = match[1];
		var param = { };
		if(match[2] !== undefined) {
			match[2].split(/&/).forEach(kv => { ((k, v) => { param[k] = decodeURIComponent(v); }).apply(null, kv.split(/=/)) });
		}
		res.writeHead(200, { 'Content-Type': 'application/json' });
		fs.readFile('var/venue-layout/frontend/'+base+'/metadata.json', { encoding: 'utf-8' }, (err, data) => {
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
	
	console.log("  -> not found");
	res.writeHead(404, { 'Content-Type': 'text/plain' });
	res.write('Not Found!');
	res.end();
};

require('http').createServer(listener)
.listen(port);
