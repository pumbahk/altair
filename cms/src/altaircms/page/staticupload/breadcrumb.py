# coding: utf-8
from altaircms.modelmanager.ancestors import GetWithGenrePagesetAncestor
from altaircms.page.models import PageSet
from altaircms.models import Genre
import json

class ParseGenre(object):

    def __init__(self, request):
        self.request = request

    def get_genre_pagesets(self):
        query = self.request.allowable(PageSet).filter(Genre.organization_id == PageSet.organization_id,
                                                       Genre.category_top_pageset_id == PageSet.id,
                                                       PageSet.event_id == None)

        genre_dict, genre_id_dict = self.list_to_dict([page for page in query.all()])

        return json.dumps(genre_dict), json.dumps(genre_id_dict)

    def list_to_dict(self, pageset_list):
        genre_dict = dict()
        genre_id_dict = dict()
        for pageset in pageset_list:
            genre_id_dict[int(pageset.genre_id)] = pageset.name
            ancestors_list = reversed(GetWithGenrePagesetAncestor(pageset).get_ancestors())
            current_dict = genre_dict
            for page in ancestors_list:
                if page.genre_id not in current_dict:
                    current_dict[int(page.genre_id)] = dict()
                else:
                    current_dict = current_dict[int(page.genre_id)]

        return genre_dict, genre_id_dict

