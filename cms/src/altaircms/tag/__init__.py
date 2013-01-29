SUPPORTED_CLASSIFIER = ("page", "asset")

def includeme(config):
    config.add_directive("add_tagmanager", ".directives.add_tagmanager")
    config.add_tagmanager("page",
                         model="altaircms.page.models.Page", 
                         xref="altaircms.page.models.PageTag2Page", 
                         tag="altaircms.page.models.PageTag"
                         )
    config.add_tagmanager("topic",
                         model="altaircms.topic.models.Topic", 
                         xref="altaircms.topic.models.TopicTag2Topic", 
                         tag="altaircms.topic.models.TopicTag"
                         )
    config.add_tagmanager("topcontent",
                         model="altaircms.topic.models.Topcontent", 
                         xref="altaircms.topic.models.TopcontentTag2Topcontent", 
                         tag="altaircms.topic.models.TopcontentTag"
                         )
    config.add_tagmanager("promotion",
                         model="altaircms.topic.models.Promotion", 
                         xref="altaircms.topic.models.PromotionTag2Promotion", 
                         tag="altaircms.topic.models.PromotionTag"
                         )
    config.add_tagmanager("asset",
                         model="altaircms.asset.models.Asset", 
                         xref="altaircms.asset.models.AssetTag2Asset", 
                         tag="altaircms.asset.models.AssetTag"
                         )
    config.add_tagmanager("image_asset",
                         model="altaircms.asset.models.ImageAsset", 
                         xref="altaircms.asset.models.AssetTag2Asset", 
                         tag="altaircms.asset.models.ImageAssetTag"
                         )
    config.add_tagmanager("flash_asset",
                         model="altaircms.asset.models.FlashAsset", 
                         xref="altaircms.asset.models.AssetTag2Asset", 
                         tag="altaircms.asset.models.FlashAssetTag"
                         )
    config.add_tagmanager("movie_asset",
                         model="altaircms.asset.models.MovieAsset", 
                         xref="altaircms.asset.models.AssetTag2Asset", 
                         tag="altaircms.asset.models.MovieAssetTag"
                         )

    config.add_route("tag", "/tag/{classifier}")

    config.scan()
