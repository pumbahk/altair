__all__ = [
    '_generate_id',
    ]

try:
    import uuid
    def _generate_id():
        return uuid.uuid4().hex
except ImportError:
    import os, time, random
    if hasattr(os, 'getpid'):
        getpid = os.getpid
    else:
        getpid = lambda: ''
    def _generate_id():
        id_str = '%f%s%f%s' % (time.time(), id({}), random.random(), getpid())
        return hashlib.md5(hashlib.md5(id_str.encode('ascii')).hexdigest()).hexdigest()
