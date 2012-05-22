def includeme(config):
    if config.registry.settings.get("altaircms.usersite.url") is None: 
        import warnings
        warnings.warn("altaircms.usersite.url is not found set to default value: http://ocalhost:5432")
        config.registry.settings["altaircms.usersite.url"] = "http://localhost:5432"

    config.add_route('front', '/publish/{page_name:.*}') # fix-url after. implemnt preview
    config.add_route("front_to_preview", "/to/preview/{page_id}")
    config.add_route('front_preview', '/preview/{page_name:.*}')
    
    config.scan('.views')
