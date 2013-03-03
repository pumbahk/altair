NIL = object()

class ModelFaker(object):
    def __init__(self, obj):
        self.__dict__["obj"] = obj
        self.__dict__["used"] = dict()

    def __getattr__(self, k, v=None):
        self.used[k] = 1
        return getattr(self.obj, k, v)

    def apply(self, k):
        v = getattr(self, k, NIL)
        if v != NIL:
            setattr(self.obj, k, v)
            
    def applyall(self):
        for k in self.used.keys():
            self.apply(k)


if __name__ == "__main__":
    class A(object):
        def __init__(self, x):
            self.x = x

    a = A(100)
    print a.x
    ma = ModelFaker(a)
    ma.x = 200
    print ma.x, a.x
    ma.apply("x")
    print ma.x, a.x
    ma.x = 300
    print ma.x, a.x
    ma.applyall()
    print ma.x, a.x
