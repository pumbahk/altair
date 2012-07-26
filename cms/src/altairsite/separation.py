# -*- coding:utf-8 -*-

from altaircms.auth.models import Organization
from altaircms.auth.interfaces import IAllowableQuery

class AllowableMyOrganizationOnly(object):
    def __init__(self, organization):
        self.organization = organization

    def _get_allowable_query(self, model, qs=None):
        query = qs or model.query
        return query.with_transformation(self.organization.inthere("organization_id"))        

    def __call__(self, request):
        return self._get_allowable_query

def query_factory_as_params(cls, auth_source, backend_id):
    organization = Organization.query.filter_by(auth_source=auth_source, backend_id=backend_id).one()
    return cls(organization)


def includeme(config):
    """
    settingsに必要なのは以下の要素。

    altairsite.organization.auth_source: 組織名のauth_source
    altairsite.organization.backend_id:  バックエンド側のid
    """

    ## allowable query(organizationごとに絞り込んだデータを提供)
    get_allowable_query = query_factory_as_params(
        AllowableMyOrganizationOnly, 
        config.registry.settings["altairsite.organization.auth_source"], 
        config.registry.settings["altairsite.organization.backend_id"])
    config.registry.registerUtility(get_allowable_query._get_allowable_query, IAllowableQuery)
    config.set_request_property(get_allowable_query, "allowable", reify=True)

    organization = get_allowable_query.organization
    config.set_request_property(lambda *args, **kwargs: organization, "organization", reify=True)
