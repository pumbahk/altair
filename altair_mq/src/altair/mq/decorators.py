import venusian

def task_config(queue="test",
                durable=True, 
                exclusive=False, 
                auto_delete=False):

    def dec(wrapped):
        def callback(scanner, name, ob):
            config = scanner.config
            config.add_task(ob,
                            queue=queue,
                            durable=durable,
                            exclusive=exclusive,
                            auto_delete=auto_delete)

        venusian.attach(wrapped, callback)
        return wrapped
    return dec
