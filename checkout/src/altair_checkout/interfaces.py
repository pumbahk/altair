from zope.interface import Interface


class ISigner(Interface):

    def __call__(checkout):
        """ 正規化XMLの署名作成する
        """
