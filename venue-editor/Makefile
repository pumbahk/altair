HTTPD=httpd
PYTHON=python

venue-editor.js: src/*.js
	$(PYTHON) compile.py -o $@ src/venue-editor.js

run: venue-editor.js
	@test -d "${PWD}/tmp" || mkdir "${PWD}/tmp"
	@$(HTTPD) -f "${PWD}/httpd.test.conf"

stop:
	@if test -e "${PWD}/tmp/pid"; then \
		kill -TERM `cat "${PWD}/tmp/pid"`; \
	else \
		echo "Server not running"; \
	fi

clean:
	rm venue-editor.js

.PHONY: run stop clean
