from fanstatic import Library, Resource
from js.jqgrid import jqgrid

altair_grid_library = Library('altair_grid', 'grid_resources')
altair_grid = Resource(altair_grid_library,
                       'altair_grid.js',
                       depends=[jqgrid])
