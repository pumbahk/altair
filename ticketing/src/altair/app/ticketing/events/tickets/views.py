# -*- coding: utf-8 -*-

import json
import sqlalchemy as sa
from altair.app.ticketing.fanstatic import with_bootstrap
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, HTTPNotFound
from altair.app.ticketing.models import DBSession, record_to_appstruct
from altair.app.ticketing.core.models import ProductItem, Performance
from altair.app.ticketing.core.models import Ticket, TicketBundle, TicketBundleAttribute
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.events.tickets.merging import TicketVarsCollector, emit_to_another_template
from altair.app.ticketing.payments.plugins.famiport import get_template_name_from_ticket_format
from altair.app.ticketing.payments.plugins.famiport import FamiPortTicketTemplate
from . import forms

import logging
logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class IndexView(BaseView):
    @view_config(route_name="events.tickets.index", renderer="altair.app.ticketing:templates/tickets/events/index.html")
    def index(self):
        event = self.context.event
        tickets = self.context.tickets
        bundles = self.context.bundles
        return dict(event=event, tickets=tickets, bundles=bundles)

    @view_config(route_name="events.tickets.api.ticketform", request_method="GET",
                 renderer="altair.app.ticketing:templates/tickets/events/_ticketform.html")
    def _api_ticketform(self):
        form = forms.BoundTicketForm(organization_id=self.context.user.organization_id)
        return dict(form=form)

    @view_config(route_name="events.tickets.api.bundleform", request_method="GET",
                 renderer="altair.app.ticketing:templates/tickets/events/_bundleform.html")
    def _api_ticketbundle_form(self):
        form = forms.BundleForm(event_id=self.request.matchdict["event_id"])
        performances = []
        return dict(form=form, performances=performances)


@view_config(route_name="events.tickets.bind.ticket", request_method="POST",
             decorator=with_bootstrap, permission="event_editor")
def bind_ticket(request):
    event = request.context.event
    organization_id = request.context.user.organization_id
    form = forms.BoundTicketForm(organization_id=organization_id,
                                 formdata=request.POST)
    if not form.validate():
        request.session.flash(u'%s' % form.errors)
        raise HTTPFound(request.route_path("events.tickets.index", event_id=event.id))

    qs = Ticket.templates_query().filter_by(organization_id=organization_id)
    ticket_template = qs.filter_by(id=form.data["ticket_template"]).one()
    bound_ticket = ticket_template.create_event_bound(event)
    bound_ticket.name = form.data["name"]
    bound_ticket.save()

    request.session.flash(u'チケットが登録されました')
    return HTTPFound(request.route_path("events.tickets.index", event_id=event.id))


@view_config(route_name='events.tickets.boundtickets.show',
             renderer='altair.app.ticketing:templates/tickets/events/tickets/show.html',
             decorator=with_bootstrap, permission="event_editor")
def show(context, request):
    qs = context.tickets_query().filter_by(id=request.matchdict['id'])
    template = qs.filter_by(organization_id=context.organization.id).first()
    if template is None:
        raise HTTPNotFound("this is not found")
    mapping_choices = [(template.id, template.name)]
    base_template_choices = [(t.id, t.name) for t in context.ticket_alls.filter(sa.or_(Ticket.event_id==None, Ticket.event_id==context.event.id))]
    transcribe_form = forms.EasyCreateTranscribeForm(mapping_id=template.id).configure(
        base_template_choices, mapping_choices)
    return dict(template=template,
                event=context.event,
                transcribe_form=transcribe_form,
                ticket_format_id=template.ticket_format_id)


@view_defaults(decorator=with_bootstrap, permission="event_editor")
class BundleView(BaseView):
    """ チケット券面構成(TicketBundle)
    """
    @view_config(route_name="events.tickets.bundles.new", request_method="POST",
                 renderer="altair.app.ticketing:templates/tickets/events/bundles/new.html")
    def bundle_new(self):
        form = forms.BundleForm(event_id=self.request.matchdict["event_id"],
                                formdata=self.request.POST)
        event = self.context.event

        if not form.validate():
            return dict(form=form, event=event)

        bundle = TicketBundle(operator=self.context.user,
                              event_id=event.id,
                              name=form.data["name"],
                              )

        bundle.replace_tickets(Ticket.filter(Ticket.id.in_(form.data["tickets"])))
        bundle.save()

        self.request.session.flash(u'チケット券面構成(TicketBundle)が登録されました')
        return HTTPFound(self.request.route_path("events.tickets.index", event_id=event.id))

    @view_config(route_name="events.tickets.bundles.edit", request_method="GET",
                 renderer="altair.app.ticketing:templates/tickets/events/bundles/new.html")
    def edit(self):
        bundle = self.context.bundle
        event = self.context.event
        form = forms.BundleForm(event_id=event.id,
                                name=bundle.name,
                                tickets=[e.id for e in bundle.tickets])
        performances = DBSession.query(Performance).join(ProductItem).filter(ProductItem.ticket_bundle==bundle)

        return dict(form=form, event=event, bundle=bundle, performances=performances)

    @view_config(route_name="events.tickets.bundles.edit", request_method="POST",
                 renderer="altair.app.ticketing:templates/tickets/events/bundles/new.html")
    def edit_post(self):
        bundle = self.context.bundle
        event = self.context.event
        form = forms.BundleForm(event_id=event.id,
                                formdata=self.request.POST)
        if not form.validate():
            return dict(form=form, event=event, bundle=bundle)

        bundle.name = form.data["name"]
        bundle.replace_tickets(Ticket.filter(Ticket.id.in_(form.data["tickets"])))
        bundle.save()

        self.request.session.flash(u'チケット券面構成(TicketBundle)が更新されました')
        return HTTPFound(self.request.route_path("events.tickets.bundles.show",
                                                 event_id=event.id, bundle_id=bundle.id))

    @view_config(route_name='events.tickets.bundles.copy', request_method="GET",
                 renderer="altair.app.ticketing:templates/tickets/events/_copyform.html")
    def copy(self):
        bundle = self.context.bundle
        event = self.context.event
        form = forms.BundleForm(event_id=event.id, name=u"%s の コピー" % bundle.name)
        next_to = self.request.route_path("events.tickets.bundles.copy",bundle_id=bundle.id, event_id=event.id)
        return dict(form=form, event=event, bundle=bundle, next_to=next_to)

    @view_config(route_name="events.tickets.bundles.copy", request_method="POST")
    def copy_post(self):
        bundle = self.context.bundle
        event = self.context.event
        form = forms.BundleForm(event_id=event.id,
                                formdata=self.request.POST)

        form.tickets.validators = []
        if not form.validate():
            self.request.session.flash(u'%s' % form.errors)
            location = self.request.route_path("events.tickets.index", event_id=event.id)
            return HTTPFound(location=location)

        new_bundle = TicketBundle(operator=self.context.user,
                                  event_id=event.id,
                                  name=form.data["name"])
        new_bundle.replace_tickets(bundle.tickets)
        #bundle.replace_tickets(Ticket.filter(Ticket.id.in_(form.data["tickets"])))
        new_bundle.save()

        for attr in TicketBundleAttribute.query.filter_by(ticket_bundle=bundle):
            new_attr = TicketBundleAttribute(name=attr.name,
                                             value=attr.value,
                                             ticket_bundle=new_bundle)
            new_attr.save()

        self.request.session.flash(u'チケット券面構成(TicketBundle)がコピーされました')
        return HTTPFound(self.request.route_path("events.tickets.bundles.show",
                                                 event_id=event.id, bundle_id=new_bundle.id))


    @view_config(route_name='events.tickets.bundles.delete', request_method="GET",
                 renderer="altair.app.ticketing:templates/tickets/events/_deleteform.html")
    def delete(self):
        bundle_id = self.request.matchdict["bundle_id"]
        event_id = self.request.matchdict["event_id"]
        message = u"このチケット券面構成(TicketBundle)を削除します。よろしいですか？"
        next_to = self.request.route_path("events.tickets.bundles.delete",bundle_id=bundle_id, event_id=event_id)
        return dict(message=message, next_to=next_to)

    @view_config(route_name='events.tickets.bundles.delete', request_method="POST")
    def delete_post(self):
        event_id = self.request.matchdict["event_id"]
        ## todo: check dangling object

        location = self.request.route_path("events.tickets.index", event_id=event_id)
        try:
            self.context.bundle.delete()
            self.request.session.flash(u'チケット券面構成(TicketBundle)を削除しました')
        except Exception, e:
            self.request.session.flash(e.message)

        return HTTPFound(location=location)

    @view_config(route_name="events.tickets.bundles.show",
                 renderer="altair.app.ticketing:templates/tickets/events/bundles/show.html")
    def show(self):
        # {<performance_id>: {<name>: "",  <products>: {}, <product_items> : {}}}
        product_item_dict = {}
        bundle = self.context.bundle

        if self.context.organization.id != 24:  # is eagles https://redmine.ticketstar.jp/issues/10928 に対する暫定対応
            for product_item in bundle.product_items:
                performance = product_item_dict.get(product_item.performance_id)
                if performance is None:
                    performance = product_item_dict[product_item.performance_id] = {
                        'name': u"%s(%s)" % (product_item.performance.name, product_item.performance.start_on),
                        'products': {},
                        'product_items': {}
                        }
                product = performance['products'].get(product_item.product.id)
                if product is None:
                    product = performance['products'][product_item.product.id] = {
                        'name': product_item.product.name,
                        'product_items': {}
                        }
                performance['product_items'][product_item.id] = \
                product['product_items'][product_item.id] = {
                    'name': product_item.name,
                    'updated_at': product_item.updated_at,
                    'created_at': product_item.created_at
                }

        # for ticket-preview
        # [{name: <performance.name>, pk: <performance.id>,  candidates: [{name: <item.name>, pk: <item.id>}, ...]}, ...]

        tickets_candidates = [{"name": t.name, "pk": t.id, "format_id": t.ticket_format_id, } for t in bundle.tickets]
        preview_item_candidates = []
        for perf_k, performance_d in product_item_dict.iteritems():
            candidates = []
            p = {"name": performance_d["name"], "pk": perf_k, "candidates": candidates}
            for item_k, item_d in performance_d["product_items"].iteritems():
                candidates.append({"name": item_d["name"], "pk": item_k, "candidates": tickets_candidates})
            preview_item_candidates.append(p)
        return dict(bundle=self.context.bundle,
                    event=self.context.event,
                    product_item_dict=product_item_dict,
                    preview_item_candidates=json.dumps(preview_item_candidates))

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class BundleAttributeView(BaseView):
    """ 属性(TicketBundleAttribute)
    """
    @view_config(route_name="events.tickets.attributes.new", request_method="GET",
                 renderer="altair.app.ticketing:templates/tickets/events/attributes/new.html")
    def new(self):
        form = forms.AttributeForm(data_value="{\n}")

        fpTicketTemplate = self.getFpTicketTemplate(self.context.bundle.tickets)

        return dict(form=form,event=self.context.event,fpTicketTemplate=fpTicketTemplate)

    @view_config(route_name="events.tickets.attributes.new", request_method="POST",
                 renderer="altair.app.ticketing:templates/tickets/events/attributes/new.html")
    def new_post(self):
        bundle = self.context.bundle
        event_id = self.request.matchdict["event_id"]
        form = forms.AttributeForm(self.request.POST, bundle_id=bundle.id)
        if not form.validate():
            return dict(form=form,event=self.context.event)

        attr = TicketBundleAttribute(name=form.data["name"],
                                     value=form.data["value"],
                                     ticket_bundle=bundle)
        attr.save()
        self.request.session.flash(u'属性(TicketBundleAttribute)を追加しました')

        return HTTPFound(self.request.route_url("events.tickets.bundles.show", event_id=event_id, bundle_id=bundle.id))

    @view_config(route_name="events.tickets.attributes.edit", request_method="GET",
                 renderer="altair.app.ticketing:templates/tickets/events/attributes/new.html")
    def edit(self):
        bundle_attribute = self.context.bundle_attribute
        form = forms.AttributeForm(name=bundle_attribute.name,
                                       value=bundle_attribute.value,
                                       bundle_id=bundle_attribute.ticket_bundle_id,
                                       attribute_id=bundle_attribute.id)

        fpTicketTemplate = self.getFpTicketTemplate(self.context.bundle.tickets)

        return dict(form=form, event=self.context.event, attribute=bundle_attribute, fpTicketTemplate=fpTicketTemplate)

    @view_config(route_name="events.tickets.attributes.edit", request_method="POST",
                 renderer="altair.app.ticketing:templates/tickets/events/attributes/new.html")
    def edit_post(self):
        attribute = self.context.bundle_attribute
        form = forms.AttributeForm(self.request.POST,
                                       bundle_id=attribute.ticket_bundle_id,
                                       attribute_id=attribute.id)


        if not form.validate():
            return dict(form=form,event=self.context.event, attribute=attribute)

        attribute.name = form.data["name"]
        attribute.value = form.data["value"]
        attribute.save()

        self.request.session.flash(u'属性(TicketBundleAttribute)を更新しました')
        kwargs = dict(event_id=self.request.matchdict["event_id"],
                      bundle_id=attribute.ticket_bundle_id)
        return HTTPFound(self.request.route_url("events.tickets.bundles.show", **kwargs))

    @view_config(route_name="events.tickets.bundles.edit_attributes", request_method="GET",
                 renderer="altair.app.ticketing:templates/tickets/events/attributes/edit.html")
    def multi_edit(self):
        attrs = TicketBundleAttribute.query.filter_by(ticket_bundle=self.context.bundle)
        form = forms.AttributesForm.append_fields(attrs)(formdata=self.request.POST, attrs=attrs)

        fpTicketTemplate = self.getFpTicketTemplate(self.context.bundle.tickets)

        return dict(event=self.context.event, bundle=self.context.bundle, form=form, fpTicketTemplate=fpTicketTemplate)

    @view_config(route_name="events.tickets.bundles.edit_attributes", request_method="POST",
                 renderer="altair.app.ticketing:templates/tickets/events/attributes/edit.html")
    def multi_edit_post(self):
        attrs = TicketBundleAttribute.query.filter_by(ticket_bundle=self.context.bundle)
        form = forms.AttributesForm.append_fields(attrs)(formdata=self.request.POST, attrs=attrs)
        for attr in attrs:
            if "attr_%u" % attr.id in form.data:
                attr.value = form.data["attr_%u" % attr.id]
                attr.save()
        names = self.request.POST.getall('newattr_names[]')
        values = self.request.POST.getall('newattr_values[]')
        if len(names) == len(values):
            for idx, name in enumerate(names):
                attr = TicketBundleAttribute(
                    name = names[idx],
                    value = values[idx],
                    ticket_bundle = self.context.bundle)
                attr.save()

        self.request.session.flash(u'属性(TicketBundleAttribute)を更新しました')
        return HTTPFound(self.request.route_url("events.tickets.index", event_id=self.request.matchdict["event_id"]))

    @view_config(route_name='events.tickets.attributes.delete', request_method="GET",
                 renderer="altair.app.ticketing:templates/tickets/events/_deleteform.html")
    def delete(self):
        attribute_id = self.request.matchdict["attribute_id"]
        bundle_id = self.request.matchdict["bundle_id"]
        event_id = self.request.matchdict["event_id"]
        message = u"この属性(TicketBundleAttribute)を削除します。よろしいですか？"
        next_to = self.request.route_path("events.tickets.attributes.delete",
                                          attribute_id=attribute_id,
                                          bundle_id=bundle_id,
                                          event_id=event_id)
        return dict(message=message, next_to=next_to)

    @view_config(route_name='events.tickets.attributes.delete', request_method="POST")
    def delete_post(self):
        event_id = self.request.matchdict["event_id"]
        bundle_id = self.request.matchdict["bundle_id"]
        self.context.bundle_attribute.delete()
        self.request.session.flash(u'"属性(TicketBundleAttribute)を削除しました')
        return HTTPFound(self.request.route_path("events.tickets.bundles.show",
                                                 event_id=event_id, bundle_id=bundle_id))

    def getFpTicketTemplate(self, tickets):
        for ticket in tickets:
            name = get_template_name_from_ticket_format(ticket.ticket_format)
            if not name is None:
                found = DBSession.query(FamiPortTicketTemplate) \
                    .filter_by(organization_id=self.context.organization.id, name=name) \
                    .first()
                if not found is None:
                    return found
        return None

def _get_base_ticket(request):
    try:
        template_kind = request.POST["template_kind"]
        preview_type = request.POST["preview_type"]
        base_template_id = request.POST["base_template_id"]
    except KeyError as e:
        raise HTTPBadRequest(str(e))

    logger.info("easycreate upload: template_kind=%s, preview_type=%s", template_kind, preview_type)
    context = request.context
    if template_kind == "event":
        return context.tickets.filter_by(id=base_template_id).first()
    elif template_kind == "base":
        return context.ticket_templates.filter_by(id=base_template_id).first()
    else:
        raise HTTPBadRequest("not support template kind {}".format(template_kind))


@view_config(route_name="events.tickets.easycreate", request_method="POST",
             decorator=with_bootstrap, permission="event_editor",
             request_param="create",
             renderer="json")
def easycreate_upload_create(context, request):
    event = context.event
    assert event.organization_id == context.organization.id

    base_ticket = _get_base_ticket(request)
    if base_ticket is None:
        raise HTTPBadRequest("base ticket is not found")

    upload_form = forms.EasyCreateTemplateUploadForm(request.POST).configure(context.event, base_ticket)
    if upload_form.validate():
        ticket_template = create_ticket_from_form(upload_form, base_ticket)
        ticket_template.save()  # flush and DBSession.add(o)
        return dict(status="ok", ticket_id=ticket_template.id)
    else:
        raise HTTPBadRequest(upload_form.errors)

@view_config(route_name="events.tickets.easycreate", request_method="POST",
             decorator=with_bootstrap, permission="event_editor",
             request_param="update",
             renderer="json")
def easycreate_upload_update(context, request):
    event = context.event
    assert event.organization_id == context.organization.id

    base_ticket = _get_base_ticket(request)
    if base_ticket is None:
        raise HTTPBadRequest("base ticket is not found")

    upload_form = forms.EasyCreateTemplateUploadForm(request.POST).configure(context.event, base_ticket)
    if upload_form.validate():
        base_ticket.data = upload_form.data_value
        formdata = upload_form.data
        base_ticket.name = formdata["name"]
        base_ticket.cover_print = formdata["cover_print"]
        base_ticket.data = upload_form.data_value
        base_ticket.save()  # flush and DBSession.add(o)
        return dict(status="ok", ticket_id=base_ticket.id)
    else:
        raise HTTPBadRequest(upload_form.errors)


@view_config(route_name="events.tickets.easycreate.transcribe", request_method="POST",
             decorator=with_bootstrap, permission="event_editor",
             renderer="json")
def easycreate_transcribe_ticket(context, request):
    event = context.event
    assert event.organization_id == context.organization.id

    try:
        base_template_id = request.POST["base_template_id"]
        mapping_id = request.POST["mapping_id"]
    except KeyError as e:
        raise HTTPBadRequest(repr(e))

    base_ticket = context.ticket_alls.filter_by(id=base_template_id).first()
    if base_ticket is None:
        raise HTTPBadRequest("base ticket is not found")
    mapping_ticket = context.tickets.filter_by(id=mapping_id).first()
    if mapping_ticket is None:
        raise HTTPBadRequest("mapping ticket is not found")

    data = record_to_appstruct(base_ticket)
    del data["id"]
    ticket = Ticket(**data)
    ticket.data["drawing"] = emit_to_another_template(base_ticket, mapping_ticket)
    ticket.data["fill_mapping"] = mapping_ticket.fill_mapping
    ticket.base_template = base_ticket
    ticket.event = context.event
    ticket.name = request.POST["name"]
    ticket.save()  # flush and DBSession.add(o)
    request.session.flash(u"チケット券面を１つ転写しました")
    return HTTPFound(location=request.route_path("events.tickets.index", event_id=context.event.id))


def create_ticket_from_form(form, base_ticket):  # xxx: todo: move to anywhere
    ticket = Ticket(
        always_reissueable=base_ticket.always_reissueable,
        principal=base_ticket.principal,
        filename="uploaded.svg",
        organization=base_ticket.organization,
    )
    formdata = form.data
    ticket.name = formdata["name"]
    ticket.ticket_format_id = formdata["ticket_format_id"]
    ticket.data = form.data_value
    ticket.cover_print = formdata["cover_print"]
    ticket.event_id = formdata["event_id"]
    # ticket.base_template_id = base_ticket.id
    ticket.base_template = base_ticket
    return ticket


@view_config(route_name="events.tickets.easycreate", request_method="GET",
             decorator=with_bootstrap, permission="event_editor",
             renderer="altair.app.ticketing:templates/tickets/events/easycreate/index.html")
def easycreate(context, request):
    event = context.event

    template_id = request.GET.get("template_id")
    if template_id:
        ticket_template = context.ticket_alls.filter_by(id=template_id).first()
    else:
        ticket_template = None

    if ticket_template is not None:
        preview_type = ticket_template.ticket_format.detect_preview_type()
        choice_form = forms.EasyCreateKindsChoiceForm(event_id=event.id, preview_type=preview_type).configure(event)
        template_form = forms.EasyCreateTemplateChoiceForm(templates=unicode(template_id))
        upload_form = forms.EasyCreateTemplateUploadForm()
    else:
        choice_form = forms.EasyCreateKindsChoiceForm().configure(event)
        template_form = forms.EasyCreateTemplateChoiceForm()
        upload_form = forms.EasyCreateTemplateUploadForm()

    event_ticket_genurl = lambda t: request.route_path("events.tickets.boundtickets.show", event_id=context.event.id, id=t.id)
    event_tickets =  [{"pk": t.id, "name": t.name, "url": event_ticket_genurl(t)} for t in context.tickets]
    base_ticket_genurl = lambda t: request.route_path("tickets.templates.show", id=t.id)
    base_tickets =  [{"pk": t.id, "name": t.name, "url": base_ticket_genurl(t)} for t in context.ticket_templates]
    return {"choice_form": choice_form,
            "template_form": template_form,
            "upload_form": upload_form,
            "event": event,
            "event_tickets": event_tickets,
            "base_tickets": base_tickets,
            "ticket_template": ticket_template
           }


@view_config(route_name="events.tickets.easycreate.loadcomponent", request_method="GET",
             decorator=with_bootstrap, permission="event_editor",
             renderer="altair.app.ticketing:templates/tickets/events/easycreate/loadcomponent.html")
def easycreate_ajax_loadcomponent(context,request):
    preview_type = request.matchdict["preview_type"]
    get = request.GET.get
    combobox_params = dict(organization_id=context.organization.id,
                           event_id=context.event.id,
                           performance_id=get("performance_id"),
                           product_id=get("product_id"),
                           )

    apis = {
        "normalize": request.route_path("tickets.preview.api", action="identity"),
        "previewbase64": request.route_path("tickets.preview.api", action="preview.base64"),
        "collectvars": request.route_path("tickets.preview.api", action="collectvars"),
        "fillvalues": request.route_path("tickets.preview.api", action="fillvalues"),
        "fillvalues_with_models": request.route_path("tickets.preview.api", action="fillvalues_with_models"),
        "combobox": request.route_path("tickets.preview.combobox"),
        "loadsvg": request.route_path("tickets.preview.loadsvg.api", model="Ticket"),
        "combobox": request.route_path("tickets.preview.combobox", _query=combobox_params)
        }
    return {"ticket_formats": [],
            "apis": apis,
            "preview_type": preview_type
    }


@view_config(route_name="events.tickets.easycreate.gettingsvg",renderer="json")
def getting_svgdata(context, request):
    preview_type = request.matchdict["preview_type"]
    ticket_id = request.matchdict["ticket_id"]
    ticket = context.ticket_alls.filter_by(id=ticket_id).first()
    if ticket is None:
        raise HTTPBadRequest("svg is not found");
    return {"svg": TicketVarsCollector(ticket).template,  "preview_type": preview_type}


@view_config(route_name="events.tickets.easycreate.gettingtemplate",renderer="json")
def getting_ticket_template_data(context, request):
    preview_type = request.matchdict["preview_type"]
    event_id = request.params.get("event_id")

    ## チケット券面発券後のみこの値が付加されてリクエストされてくる。コレを先頭に持ってくる
    created_template_id = request.params.get("template_id")

    if event_id:
        assert unicode(context.event.id) == unicode(event_id)
        tickets = context.tickets
    else:
        tickets = context.ticket_templates

    if preview_type == "sej":
        tickets = list(context.filter_sej_ticket_templates(tickets))
    else:
        tickets = list(context.filter_something_else_ticket_templates(tickets))

    if created_template_id:
        ## todo: 移動。合致したidを持つobjectを先頭に移動している
        idx = None
        for i, t in enumerate(tickets):
            if unicode(t.id) == unicode(created_template_id):
                idx = i
                break
        if idx:
            selected = tickets.pop(idx)
            tickets.insert(0, selected)

    return {
        "iterable": [{"pk": t.id, "name": t.name, "checked": False} for t in tickets],
        "tickets": {t.id:{"pk": t.id, "name": t.name, "cover_print":t.cover_print, "principal":t.principal, "always_reissueable": t.always_reissueable} for t in tickets}
    }


@view_config(route_name="events.tickets.easycreate.gettingformat",renderer="json")
def getting_ticket_format_data(context, request):
    preview_type = request.matchdict["preview_type"]
    if preview_type == "sej":
        qs = context.ticket_sej_formats
    else:
        qs = context.ticket_something_else_formats
    D = {t.id: {"pk": t.id, "name": t.name, "type": preview_type} for t in qs}
    return {"iterable": list(D.values()), "preview_type": preview_type}


@view_config(route_name="events.tickets.easycreate.gettingvarsvals", renderer="json")
def getting_getting_vars_values(context, request):
    ticket_id = request.matchdict["ticket_id"]
    ticket = context.ticket_alls.filter_by(id=ticket_id).first()
    if ticket is None:
        raise HTTPBadRequest("svg is not found")
    return {"params": TicketVarsCollector(ticket).collect()}
