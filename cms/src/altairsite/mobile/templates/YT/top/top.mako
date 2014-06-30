<%inherit file="../common/_base.mako" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<%block name="title">チケットトップ</%block>

<div>
├<a href="/howto">購入方法</a><br>
├<a href="/help">FAQ</a><br>
├<a href="/orderreview">購入確認</a><br>
└<a href="http://www.ytj.gr.jp/">公式サイトへ</a><br>
</div>
<br />

<%
    if form.promotions.data:
        promotions = [(event, promo) for event, promo in ((helper.get_event_from_linked_page_id(request, promo.linked_page_id), promo) for promo in form.promotions.data)]
%>

<%m:header>注目公演</%m:header>
% if form.promotions.data:
    % for event, promo in promotions:
        <%
            link = None
            if promo.mobile_link:
                link = promo.mobile_link
            elif event:
                link = request.mobile_route_path("eventdetail") + "?event_id=" + str(event.id)
        %>
        % if link:
            <a href=${link}>${promo.text}</a><br />
        % else:
            % if helper.get_eventsqs_from_mobile_tag_id(request, promo.mobile_tag_id).all():
                <a href="${request.mobile_route_path('mobile_tag_search', mobile_tag_id=promo.mobile_tag_id, genre=0, sub_genre=0, page=1)}">${promo.text}</a><br/>
            % else:
                ${promo.text}<br/>
            % endif
        % endif
    % endfor
% endif

<%include file="../common/_attention.mako" args="attentions=form.attentions.data, genre=0, sub_genre=0, helper=helper"/>
