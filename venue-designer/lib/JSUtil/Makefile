# macro
MYSRCS	= \
	package.js		\
	util.error.js		\
	Console.js		\
	JSONParser.js

ROOTSRC = package.js

# proc
.PHONY:	all clean

all:	cmp

clean:
	rm -rf JSUtil.js

cmp:	$(MYSRCS)
	export REQUEST_METHOD="GET" QUERY_STRING="file=$(ROOTSRC)"; ./compile.py -c > JSUtil.js
