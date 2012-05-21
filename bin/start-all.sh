pserve ../cms/production.ini --reload --daemon --pid-file="cms.pid" --log-file="../logs/cms.log" http_port=6543
pserve ../cms/usersite.production.ini --reload --daemon --pid-file="usersite.pid" --log-file="../logs/usersite.log" http_port=5432
pserve ../ticketing/src/development.ini --reload --daemon --pid-file="ticketing.pid" --log-file="../logs/ticketing.log" http_port=7654
## todo fix ticketing ini file (development.ini ->  production.ini)
