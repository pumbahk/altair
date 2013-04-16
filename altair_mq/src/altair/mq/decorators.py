import venusian

def task_config():
    def dec(wrapped):
        def callback(scanner, name, ob):
            pass
        venusian.attatch(wrapped, callback)
        return wrapped
    return dec
