from . import proxy
def clone(session, page, wtree):
    D = {}
    for bname, ws in wtree.blocks.items():
        D[bname] = [w.clone(session, page) for w in ws]
    return proxy.WidgetTree(blocks=D)

def to_structure(wtree):
    return {bname: [dict(name=w.type, pk=w.id) for w in ws]\
                for bname, ws in wtree.blocks.items()}
