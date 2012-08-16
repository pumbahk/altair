HTTPD=httpd
PYTHON=python

venue-viewer.js: src/*.js
	$(PYTHON) compile.py -o $@ src/venue-viewer.js

run: venue-viewer.js
	@test -d "${PWD}/tmp" || mkdir "${PWD}/tmp"
	@$(HTTPD) -f "${PWD}/httpd.test.conf"

stop:
	@if test -e "${PWD}/tmp/pid"; then \
		kill -TERM `cat "${PWD}/tmp/pid"`; \
	else \
		echo "Server not running"; \
	fi

clean:
	rm venue-viewer.js

.PHONY: run stop clean
