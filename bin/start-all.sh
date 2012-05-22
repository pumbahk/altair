pserve ../cms/deploy/production.ini --reload --daemon --pid-file="cms.pid" --log-file="../logs/cms.log" http_port=8001
pserve ../cms/deploy/usersite.production.ini --reload --daemon --pid-file="usersite.pid" --log-file="../logs/usersite.log" http_port=8003
