from resources import SampleCoreResource
def me():
    return __package__

def includeme(config):
    config.add_route("sample::create_page", "/page/create", factory=SampleCoreResource)
    config.add_route("sample::edit_page", "/page/{page_id}/edit", factory=SampleCoreResource)
    config.add_route("sample::sample", "/sample")
    config.add_route("sample::freetext", "/freetext")

    ##
    config.add_route("ok", "/result/ok", factory=SampleCoreResource)

