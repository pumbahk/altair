def includeme(config):
    """
    list
    create : input -> confirm -> create
    update : input -> confirm -> update
    delete : confirm -> update
    """
    config.add_directive("add_crud", ".directives.add_crud")
