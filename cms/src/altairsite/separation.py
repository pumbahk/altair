# -*- coding:utf-8 -*-

import functools
from altaircms.auth.interfaces import IAllowableQueryFactory
from zope.interface import implementer
from altaircms.auth.models import Organization

@implementer(IAllowableQueryFactory)
class AllowableMyOrganizationOnly(object):
    def __init__(self, model, organization):
        self.model = model
        self.organization = organization

    def __call__(self, request, query=None):
        query = query or self.model.query
        return query.with_transformation(self.organization.inthere("organization_id"))

def query_factory_as_params(cls, auth_source, backend_id, model):
    organization = Organization.query.filter_by(auth_source=auth_source, backend_id=backend_id).one()
    return cls(model, organization)

def includeme(config):
    """
    settingsに必要なのは以下の要素。

    altairsite.organization.auth_source: 組織名のauth_source
    altairsite.organization.backend_id:  バックエンド側のid
    """

    ## allowable query(organizationごとに絞り込んだデータを提供)
    config.set_request_property("altaircms.auth.api.get_allowable_query", "allowable", reify=True)

    query_factory = functools.partial(
        query_factory_as_params, 
        AllowableMyOrganizationOnly, 
        config.registry.settings["altairsite.organization.auth_source"], 
        config.registry.settings["altairsite.organization.backend_id"])
    
    def register_allowable(modelname, callname):
        """ request.allowable("<call-name>")で呼べるようにモデルを登録する"""
        allowable_query_factory = query_factory(config.maybe_dotted(modelname))
        config.registry.registerUtility(allowable_query_factory, IAllowableQueryFactory, name=callname)

    register_allowable("altaircms.asset.models.Asset", "Asset")
    register_allowable("altaircms.asset.models.ImageAsset", "ImageAsset")
    register_allowable("altaircms.asset.models.MovieAsset", "MovieAsset")
    register_allowable("altaircms.asset.models.FlashAsset", "FlashAsset")
    register_allowable("altaircms.event.models.Event", "Event")
    register_allowable("altaircms.page.models.Page", "Page")
    register_allowable("altaircms.page.models.PageSet", "PageSet")
    register_allowable("altaircms.widget.models.WidgetDisposition", "WidgetDisposition")
    register_allowable("altaircms.layout.models.Layout", "Layout")
    register_allowable("altaircms.plugins.widget.promotion.models.PromotionUnit", "PromotionUnit")
    register_allowable("altaircms.plugins.widget.promotion.models.Promotion", "Promotion")
    register_allowable("altaircms.models.Category", "Category")
    register_allowable("altaircms.topic.models.Topic", "Topic")
    register_allowable("altaircms.topic.models.Topcontent", "Topcontent")
    register_allowable("altaircms.tag.models.HotWord", "HotWord")
    register_allowable("altaircms.tag.models.PageTag", "PageTag")
    register_allowable("altaircms.tag.models.AssetTag", "AssetTag")
    register_allowable("altaircms.tag.models.ImageAssetTag", "ImageAssetTag")
    register_allowable("altaircms.tag.models.MovieAssetTag", "MovieAssetTag")
    register_allowable("altaircms.tag.models.FlashAssetTag", "FlashAssetTag")
    register_allowable("altaircms.auth.models.Operator", "Operator")
