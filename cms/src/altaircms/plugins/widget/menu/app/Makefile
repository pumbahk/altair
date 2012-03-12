SRC = __init__.py

deactivate:
	(test -f ${SRC}.pyc && rm ${SRC}.pyc) || echo 0
	test -f ${SRC} && mv ${SRC} ${SRC}.dead

activate:
	test -f ${SRC}.dead && mv ${SRC}.dead ${SRC}
