from . import PC_ACCESS_COOKIE_NAME
from datetime import datetime #ok?

## for smartphone
def set_we_need_pc_access(response):
    response.set_cookie(PC_ACCESS_COOKIE_NAME, str(datetime.now()))

def set_we_invalidate_pc_access(response):
    response.delete_cookie(PC_ACCESS_COOKIE_NAME)
    
