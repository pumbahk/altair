import re
import time
from datetime import date, timedelta

def is_drawing_compressed(drawing):
    return re.match('^.+\.(svgz|gz)$', drawing.path)

def get_s3_url(drawing):
    key = drawing.get_key()
    headers = {}
    if is_drawing_compressed(drawing):
        headers['response-content-encoding'] = 'gzip'
    expire_date = date.today() + timedelta(days=2)
    expire_epoch = time.mktime(expire_date.timetuple())
    return key.generate_url(expires_in=expire_epoch, expires_in_absolute=True, response_headers=headers)
