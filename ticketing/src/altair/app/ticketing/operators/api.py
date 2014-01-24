import hashlib

def crypt(passwd):
    return hashlib.md5(passwd).hexdigest() # FIXME
