from pkg_resources import resource_filename, EntryPoint
import os

def import_symbol(symbol):
    """import a content of module from a module name string

    module name string format:
      foo.bar.baz:symbol_name 
      foo.bar.baz
    """
    return EntryPoint.parse("x=%s" % symbol).load(False)

def collect_files(root, p):
    for prefix, dires, files in os.walk(root):
        for f in files:
            if p(f):
                fullpath = os.path.join(prefix, f)
                yield fullpath

def moduleformat(root, rootmodule, path):
    """foo/bar/baz.py -> foo.bar.baz"""
    replaced = path.replace(root, rootmodule)
    return os.path.splitext(replaced)[0].replace("/", ".")

def import_model_modules(rootmodule, model_filename):
    root = resource_filename(rootmodule, "")
    for path in collect_files(root, lambda f: f.endswith(model_filename) and not "test" in f):
        import_symbol(moduleformat(root, rootmodule, path))



def insert_permission_data(session):
    from altaircms.auth.models import Role, DEFAULT_ROLE, PERMISSIONS
    import transaction

    # administrator
    role = Role(name=DEFAULT_ROLE, permissions=PERMISSIONS)
    session.add(role)

    perms = ["_create", "_read", "_delete", "_update"]
    for target in ['event', 'topic', 'topcontent', 'ticket', 'magazine', 'asset', 'page', 'tag', 'promotion', 'promotion_unit', 'performance', 'layout', 'operator', "hotword"]:
        # viewer
        role = Role(name=target + "_viewer", permissions=[target + "_read"])
        session.add(role)
        # editor
        role = Role(name=target + "_editor", permissions=[(target + perm) for perm in perms])
        session.add(role)
    transaction.commit()

def includeme(config):
    import sqlahelper
    from sqlalchemy import engine_from_config

    settings = config.registry.settings
    engine = engine_from_config(settings, 'sqlalchemy.')

    sqlahelper.add_engine(engine)
    sqlahelper.get_session().remove()

    import_model_modules("altaircms", "models.py")
    sqlahelper.get_base().metadata.create_all()

    session = sqlahelper.get_session()
    insert_permission_data(session)
