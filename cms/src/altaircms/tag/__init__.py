SUPPORTED_CLASSIFIER = ("page", "event", "asset")

def includeme(config):
    config.add_directive("add_tagmanager", ".directives.add_tagmanager")
    config.add_tagmanager("page",
                         model="altaircms.page.models.Page", 
                         xref=".models.PageTag2Page", 
                         tag=".models.PageTag"
                         )
    config.add_tagmanager("event",
                         model="altaircms.event.models.Event", 
                         xref=".models.EventTag2Event", 
                         tag=".models.EventTag"
                         )
    config.add_tagmanager("asset",
                         model="altaircms.asset.models.Asset", 
                         xref=".models.AssetTag2Asset", 
                         tag=".models.AssetTag"
                         )
    config.add_tagmanager("image_asset",
                         model="altaircms.asset.models.ImageAsset", 
                         xref=".models.AssetTag2Asset", 
                         tag=".models.ImageAssetTag"
                         )
    config.add_tagmanager("flash_asset",
                         model="altaircms.asset.models.FlashAsset", 
                         xref=".models.AssetTag2Asset", 
                         tag=".models.FlashAssetTag"
                         )
    config.add_tagmanager("movie_asset",
                         model="altaircms.asset.models.MovieAsset", 
                         xref=".models.AssetTag2Asset", 
                         tag=".models.MovieAssetTag"
                         )
    

    config.add_route("tag", "/tag/{classifier}")
