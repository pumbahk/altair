SRC = __init__.py

deactivate:
	(test -f ${SRC}c && rm ${SRC}c) || echo 0
	test -f ${SRC} && mv ${SRC} ${SRC}.dead

activate:
	test -f ${SRC}.dead && mv ${SRC}.dead ${SRC}
