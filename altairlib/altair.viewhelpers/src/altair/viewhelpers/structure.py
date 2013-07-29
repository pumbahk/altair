def updated(*ds):
    D = {}
    for d in ds:
        D.update(d)
    return D

def merged(d1, **kwargs):
    D = d1.copy()
    D.update(kwargs)
    return D

