import venusian

def task_config():
    def dec(wrapped):
        def callback(scanner, name, ob):
            config = scanner.config
            config.add_task(ob)
        venusian.attach(wrapped, callback)
        return wrapped
    return dec
