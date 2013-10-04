# -*- coding:utf-8 -*-

"""
KeyBreak
------------------------------

"""



class KeyBreak(object):
    def __init__(self, keys):
        self.keys = keys

    def __call__(self, data):
        marker = object()
        #last_data = data[0] if len(data) else dict()
        last_data = dict()
        last_data.setdefault(marker)
        for i, d in enumerate(data):
            if i == 0:
                yield dict([(k, False) for k in self.keys]), d
            else:
                yield dict([(k, d.get(k) != last_data.get(k)) for k in self.keys]), d
            last_data = d

class PredicatedYielder(object):
    """ 多分1つ目のキーが変わったときにためた値をyieldさせるのに使う
    """
    def __init__(self, predicate):
        self.predicate = predicate

    def __call__(self, iter):
        for i in iter:
            if self.predicate(i):
                yield i

class KeyBreakCounter(object):
    def __init__(self, keys):
        self.breaker = KeyBreak(keys)
        self.keys = keys

    def __call__(self, data):
        """ あるキーが変わったらそこをカウントアップ
        あるキーの上位が変わったらリセット
        複数キーがカウントアップされることはない

        キーチェンジリストから最初のTrueの位置をさがす
        その位置のカウントをアップ
        それより後ろを0にリセット
        """

        counter = dict([(k, 0) for k in self.keys])

        for key_changes, d in self.breaker(data):
            key_changes_l = [key_changes.get(k) for k in self.keys]
            if True in key_changes_l:
                i = key_changes_l.index(True)
                counter = dict([(k, counter[k]) for k in self.keys[:i]]
                               + [(self.keys[i], counter[self.keys[i]] + 1)] 
                               + [(k, 0) for k in self.keys[i+1:]])
            yield counter, key_changes, d
