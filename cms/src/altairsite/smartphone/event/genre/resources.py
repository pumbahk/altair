# -*- coding:utf-8 -*-
from altairsite.smartphone.resources import TopPageResource
from altaircms.models import Genre

class GenrePageResource(TopPageResource):
    def get_genre(self, id):
        genre = self.request.allowable(Genre).filter(Genre.id==id).first()
        return genre
