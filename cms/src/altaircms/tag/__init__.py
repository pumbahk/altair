def includeme(config):
    config.add_directive("add_tagsearch", ".directives.add_tagsearch")
    config.add_tagsearch("page",
                         model="altaircms.page.models.Page", 
                         xref=".models.PageTag2Page", 
                         tag=".models.PageTag"
                         )
    config.add_tagsearch("event",
                         model="altaircms.event.models.Event", 
                         xref=".models.EventTag2Event", 
                         tag=".models.EventTag"
                         )
    config.add_tagsearch("asset",
                         model="altaircms.asset.models.Asset", 
                         xref=".models.AssetTag2Asset", 
                         tag=".models.AssetTag"
                         )
    config.add_tagsearch("image_asset",
                         model="altaircms.asset.models.ImageAsset", 
                         xref=".models.AssetTag2Asset", 
                         tag=".models.ImageAssetTag"
                         )
    config.add_tagsearch("flash_asset",
                         model="altaircms.asset.models.FlashAsset", 
                         xref=".models.AssetTag2Asset", 
                         tag=".models.FlashAssetTag"
                         )
    config.add_tagsearch("movie_asset",
                         model="altaircms.asset.models.MovieAsset", 
                         xref=".models.AssetTag2Asset", 
                         tag=".models.MovieAssetTag"
                         )
    
