from pyramid.decorator import reify
from ..models import Genre, _GenrePath

class GenreSearcher(object):
    def __init__(self, request):
        self.request = request

    @reify
    def root(self):
        return self.request.allowable(Genre).filter(Genre.is_root==True).first()

    def query_genre_root(self):
        return self.request.allowable(Genre)\
            .join(_GenrePath, _GenrePath.genre_id==Genre.id)\
            .filter(_GenrePath.next_id==self.root.id)

    def get_top_genre_list(self):
        return self.query_genre_root().all()

    def get_children(self, genre):
        return genre.children
