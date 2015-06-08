import os

def normal_file_filter(dir, l):
    return [f for f in l if os.path.isfile(os.path.join(dir, f))]

class ImportSession(object):
    def __init__(self, pending_dir, imported_dir, file_filter, processor, logger):
        self.pending_dir = pending_dir
        self.imported_dir = imported_dir
        self.file_filter = file_filter
        self.processor = processor
        self.logger = logger

    def lookup_targets(self):
        l = os.listdir(self.pending_dir)
        if self.file_filter is not None:
            l = self.file_filter(self.pending_dir, l)
        return l

    def __call__(self):
        l = self.lookup_targets()
        retval = []
        for _f in l:
            f = os.path.join(self.pending_dir, _f)
            try:
                _nf = self.processor(f)
            except Exception as e:
                self.logger.exception('failed to process %s' % f)
                continue
            if _nf is not None:
                nf = os.path.join(self.imported_dir, _nf)
            else:
                nf = os.path.join(self.imported_dir, _f)
            os.rename(f, nf)
            retval.append(nf)
        return retval        
