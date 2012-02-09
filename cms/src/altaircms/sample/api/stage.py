NEW = 0
LAYOUT_SELECTED = 1
WIDGETS_SELECTED = 2
DATA_EDITED = 3

class StageInfo(object):
    def __init__(self, storage):
        self.stage = self._get_stage(storage)
        self.layoutname = storage.layout
        self.storage = storage

    def _get_stage(self, storage):
        if storage.layout is None:
            return NEW
        elif len(storage.blocks.blocks) <= 1:
            return LAYOUT_SELECTED
        else:
            return WIDGETS_SELECTED

    @property
    def context(self):
        """
        output:
        [{
            'widgets': [{"widget_name": "image_widget", "data": {"image_file": "/statics/img/foo.png"}}], 
            'block_name': 'selected_center'
         }, 
         {
            'widgets': [{"widget_name": "dummy_widget", "data": {}}], 
            'block_name': 'selected_header'
         }]
        """
        r = []
        for block_name, npb in self.storage.blocks.iteritems():
            if not block_name.startswith("*"): #"*layout*" is special name
                r.append(dict(block_name=block_name, widgets=[x for x in npb]));
        return r
        
def get_stage(storage):
    return StageInfo(storage)

