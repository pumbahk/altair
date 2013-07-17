## fetch svg from model id
## svg transformation
import logging
logger = logging.getLogger(__name__)
from .validators import parse, FetchSVGFromModelsValidator

#give me Maybe..
def fetch_svg_from_postdata(postdata):
    data = parse(FetchSVGFromModelsValidator, postdata or {})
    if data is None:
        return None
    model = data["model"]
    if model is None:
        return None
    model_data = model.data
    if model_data is None:
        return None
    return model_data.get("drawing")
