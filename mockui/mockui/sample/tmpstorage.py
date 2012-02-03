### api views
from collections import defaultdict
from structures import OrderedBlocks
import os
import pickle
import logging
import sys

logger = logging.getLogger(__name__)

class Storage(object):
    def __init__(self):
        self.layout = None
        self.blocks = self._refresh()

    def _refresh(self):
        self.blocks = defaultdict(dict)

    def save_layout(self, layout_name):
        self.layout = layout_name
        self._refresh()

    def save_block(self, block_name, orderno, widget_name):
        self.blocks[block_name][orderno] = widget_name
        logger.debug(self.blocks)
    
    def move_block(self, oldblock,  old_orderno, block_name, orderno):
        if not oldblock == block_name and old_orderno == orderno:
            widget_name = self.blocks[oldblock][orderno]
            self.save_block(block_name, orderno, widget_name)
            del self.blocks[oldblock][orderno]
            logger.debug(self.blocks)

    def load_block(self, block_name, orderno):
        return self.blocks[block_name][orderno]
        logger.debug(self.blocks)
        

### signal trap

def _normalize(method):
    def decorated(self, *args):
        args_ = [str(x) if isinstance(x, basestring) else x for x in args]
        return unicode(method(self, *args_))
    return decorated

class ShelveStorage(object):
    def _sync(self):
        sys.stderr.write("writing to file...(./shelve.dat)\n")
        pickle.dump(self.blocks, open(self.fname, "w"))

        
    def capture_signal(self):
        import signal
        def handler(signum, frame):
            self._sync()
            
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)


    def __init__(self, fname="shelve.dat"):
        self.fname = fname
        self.layout = None
        self.blocks = self._setup()
        if self.blocks["*layout*"].xs:
            self.layout = self.blocks["*layout*"].xs[0]

    def _setup(self):
        if os.path.exists(self.fname):
            r = pickle.load(open(self.fname))
        else:
            r = OrderedBlocks()
        logging.debug(r)
        return r

    def _refresh(self):
        if os.path.exists(self.fname):
            os.remove(self.fname)
        self.blocks = self._setup()

    @_normalize
    def save_layout(self, layout_name):
        self.layout = layout_name
        self._refresh()
        self.blocks["*layout*"] = self.layout
        logging.debug(self.blocks)

    @_normalize
    def save_block(self, block_name, orderno, widget_name): #orderno?
        ## add block
        self.blocks.add(block_name, widget_name)
        logger.debug(self.blocks)


    @_normalize
    def move_block(self, oldblock,  old_orderno, block_name, orderno): #orderno?
        if not (oldblock == block_name and old_orderno == orderno):
            widget_name = self.blocks[oldblock].get_by_orderno(int(old_orderno))
            self.blocks.move(oldblock, block_name, widget_name)
            logger.debug(self.blocks)

    @_normalize
    def load_block(self, block_name, orderno):
        logger.debug(self.blocks)
        return self.blocks[block_name].get_by_orderno(int(orderno))

    @_normalize
    def delete_widget(self, block_name, orderno):
        widget_name = self.blocks[block_name].get_by_orderno(int(orderno))
        self.blocks.delete(block_name, widget_name)
        logger.debug(self.blocks)


_storage = ShelveStorage()
_storage.capture_signal()

def get_storage():
    global _storage
    return _storage
