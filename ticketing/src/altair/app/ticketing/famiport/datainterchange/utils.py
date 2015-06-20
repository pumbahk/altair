import os

def make_room(base_dir): 
    def _(dir_, serial=0):
        if os.path.exists(dir_):
            next_dir = '%s.%d' % (base_dir, serial)
            _(next_dir, serial + 1)
            os.rename(dir_, next_dir)
    _(base_dir)
