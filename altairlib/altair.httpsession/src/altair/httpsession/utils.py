def asbool(v):
    if isinstance(v, basestring):
        try:
            return bool(int(v))
        except (ValueError, TypeError):
            pass
        v = v.lower()
        return v in ('true', 'yes')
    else:
        return bool(v)
