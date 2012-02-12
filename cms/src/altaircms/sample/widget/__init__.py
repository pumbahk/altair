from altaircms.sample.resources import SampleResource

def includeme(config):
    ## widget view
    config.add_route("sample::image_widget", "/api/load/widget/image", factory=SampleResource)
    config.add_route("sample::freetext_widget", "/api/load/widget/freetext", 
                     factory=SampleResource)

