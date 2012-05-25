HTTPD=httpd

run: lib/Fashion/fashion.js build/out.js
	$(HTTPD) -X -f ${PWD}/httpd.test.conf

lib/Fashion/fashion.js:
	$(MAKE) -C lib/Fashion

build/out.js:
	$(MAKE) -C src

.PHONY: run
