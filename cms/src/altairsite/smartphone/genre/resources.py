# -*- coding:utf-8 -*-
from ..common.resources import CommonResource

class GenrePageResource(CommonResource):

    def is_sub_sub_genre(self, genre_id):
        genre = self.get_genre(genre_id)
        for path in genre._parents:
            if path.hop == 3:
                return True
        return False