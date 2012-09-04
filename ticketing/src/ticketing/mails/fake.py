import logging
logger = logging.getLogger(__name__)

class FakeObject(unicode):
    @classmethod
    def create(cls, name="*", **kwargs):
        o = cls(name)
        for k, v in kwargs.iteritems():
            o.__dict__[k] = v
        return o
        
    def __init__(self, name="*"):
        self.name = name
        self.items = {}

    def __repr__(self):
        return "%r %s" % (self.__class__, self.name)

    def __create_child__(self, name):
        longname = "%s.%s" % (self.name , name)
        return self.__class__(longname)

    def __getattr__(self, name):
        child = self.__create_child__(name) ## object
        setattr(self, name, child)
        return child

    def __getitem__(self, name):
        v = self.items.get(name)
        if v is None:
            v = self.items[name] = self.__create_child__(name) ## Dict
        return v

    def __iter__(self):
        return iter([])

    def __str__(self):
        return self.name

    def __int__(self):
        return 0

    def __float__(self):
        return 0.0

    def __call__(self, *args, **kwargs):
        logger.debug("warn call() return self")
        return self
