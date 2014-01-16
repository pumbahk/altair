#-*- coding: utf-8 -*-
from wtforms import (
    Form,
    FileField,
    )
from altair.formhelpers import (
    Required,
    Translations
    )
    
class AugusVenueUploadForm(Form):
    augus_venue_file = FileField(
        label=u'CSVファイル',
        validators=[],
    )
