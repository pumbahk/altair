from pyramid.response import _BLOCK_SIZE, FileIter, Response

## almost copy of pyramid.response.FileResponse
class FileLikeResponse(Response):
     def __init__(self, io, request=None, cache_max_age=None,
                 content_type=None, content_encoding=None):
        super(FileLikeResponse, self).__init__(conditional_response=True)
        if content_type is None:
            content_type = 'application/octet-stream'
        self.content_type = content_type
        self.content_encoding = content_encoding
        content_length = io.len
        app_iter = None
        if request is not None:
            environ = request.environ
            if 'wsgi.file_wrapper' in environ:
                app_iter = environ['wsgi.file_wrapper'](io, _BLOCK_SIZE)
        if app_iter is None:
            app_iter = FileIter(io, _BLOCK_SIZE)
        self.app_iter = app_iter
        # assignment of content_length must come after assignment of app_iter
        self.content_length = content_length
        if cache_max_age is not None:
            self.cache_expires = cache_max_age
