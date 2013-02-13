from .searcher import GenreSearcher

def get_searcher(request):
    return GenreSearcher(request)
