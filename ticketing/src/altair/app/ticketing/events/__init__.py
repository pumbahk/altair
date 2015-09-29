# -*- coding: utf-8 -*-
from altair.app.ticketing import newRootFactory
from .resources import EventAdminResource

def includeme(config):
    factory = newRootFactory(EventAdminResource)
    config.add_route('events.index', '/', factory=factory)
    config.add_route('events.visible', '/visible', factory=factory)
    config.add_route('events.invisible', '/invisible', factory=factory)
    config.add_route('events.new', '/new', factory=factory)
    config.add_route('events.show', '/show/{event_id}', factory=factory)
    config.add_route('events.show.performances.visible', '/show/performances/visible/{event_id}', factory=factory)
    config.add_route('events.show.performances.invisible', '/show/performances/invisible/{event_id}', factory=factory)
    config.add_route('events.edit', '/edit/{event_id}', factory=factory)
    config.add_route('events.copy', '/copy/{event_id}', factory=factory)
    config.add_route('events.delete', '/delete/{event_id}', factory=factory)
    config.add_route('events.send', '/send/{event_id}', factory=factory)
    config.add_route('events.open', '/open/{event_id}/{public}', factory=factory)
    config.add_route('events.famiport.performance_groups.index', '/{event_id}/famiport/performance_groups', factory=factory)
    config.add_route('events.famiport.performance_groups.item.show', '/{event_id}/famiport/performance_groups/{altair_famiport_performance_group_id}/show', factory=factory)
    config.add_route('events.famiport.performance_groups.item.edit', '/{event_id}/famiport/performance_groups/{altair_famiport_performance_group_id}/edit', factory=factory)
    config.add_route('events.famiport.performances.item.show', '/{event_id}/famiport/performance_groups/{altair_famiport_performance_group_id}/performances/{altair_famiport_performance_id}/show', factory=factory)
    config.add_route('events.famiport.performances.item.edit', '/{event_id}/famiport/performance_groups/{altair_famiport_performance_group_id}/performances/{altair_famiport_performance_id}/edit', factory=factory)
    config.add_route('events.famiport.performances.item.delete', '/famiport/performance_groups/performances/{altair_famiport_performance_id}/delete', factory=factory)
    config.add_route('events.famiport.performance_groups.action', '/{event_id}/famiport/performance_groups/*traverse', factory=factory)

    config.include('altair.app.ticketing.events.performances', route_prefix='performances')
    config.include('altair.app.ticketing.events.sales_segment_groups', route_prefix='sales_segment_groups')
    config.include('altair.app.ticketing.events.sales_segments', route_prefix='sales_segments')
    config.include('altair.app.ticketing.events.payment_delivery_method_pairs', route_prefix='payment_delivery_method_pairs')
    config.include('altair.app.ticketing.events.stock_holders', route_prefix='stock_holders')
    config.include('altair.app.ticketing.events.stock_types' , route_prefix='stock_types')
    config.include('altair.app.ticketing.events.stocks' , route_prefix='stocks')
    config.include('altair.app.ticketing.events.tickets', route_prefix='tickets')
    config.include('altair.app.ticketing.events.mailinfo', route_prefix='mailinfo')
    config.include('altair.app.ticketing.events.reports', route_prefix='reports')
    config.include('altair.app.ticketing.events.sales_reports', route_prefix='sales_reports')
    config.include('altair.app.ticketing.events.lots', route_prefix='lots')
    config.include('altair.app.ticketing.events.cooperation', route_prefix='cooperation')
    config.scan(".")

VISIBLE_EVENT_SESSION_KEY = "_visible_event"
