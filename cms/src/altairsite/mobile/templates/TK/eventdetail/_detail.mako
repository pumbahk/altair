<%namespace file="../common/tags_mobile.mako" name="m" />
<%page args="event, week, month_unit, month_unit_keys, purchase_links, tickets, sales_start, sales_end, helper" />
<%
    perfs = []
    for perf in event.performances:
        if perf.public:
            perfs.append({"perf":perf, "display_order":perf.display_order})
    perfs = sorted(perfs, key=lambda v: (v['display_order']))
    from altaircms.datelib import get_now

    o = event.event_open
    c = event.event_close
    period = helper.get_info(event_info, u'公演期間') or str(o.year) + u"/" + str(o.month).zfill(2) + u"/" + str(o.day).zfill(2) + u"(" + week[o.weekday()] + u") 〜 " + str(c.year) + u"/" + str(c.month).zfill(2) + u"/" + str(c.day).zfill(2) + u"(" + week[c.weekday()] + u")"
    if o.year==c.year and o.month==c.month and o.day==c.day:
        period = str(o.year) + u"/" + str(o.month).zfill(2) + u"/" + str(o.day).zfill(2) + u"(" + week[o.weekday()] + u")"

    info = {
        'performance_period':period,
        'performers':helper.get_info(event_info, u'出演者') or event.performers,
        'salessegment':helper.get_info_list(event_info, u'販売期間') ,
        'notice':helper.get_info(event_info, u'説明／注意事項') or event.notice,
        'ticket_payment':helper.get_info(event_info, u'お支払い方法') ,
        'ticket_pickup':helper.get_info(event_info, u'チケット引き取り方法') ,
        'content':helper.get_info(event_info, u'お問い合わせ先') or event.inquiry_for,
    }
%>


<%def name="render_sale(segment)">
    % if segment.find(u"先行抽選") != -1:
        先行抽選
    % elif segment.find(u"先行先着") != -1:
        先行先着
    % elif segment.find(u"一般販売") != -1:
        一般販売
    % elif segment.find(u"一般発売") != -1:
        一般発売
    % elif segment.find(u"先行販売") != -1:
        先行販売
    % endif
</%def>

<%m:header>公演期間</%m:header>
${helper.nl2br(info['performance_period'])|n}<br/>
<br/>

<%m:header>販売期間</%m:header>
% if info['salessegment']:
    % for segment in info['salessegment']:
        ${render_sale(segment[0])}:${helper.nl2br(segment[1])|n}
        <br/>
    % endfor
    <br />
% else:

    % if event.salessegment_groups:
        % for sales_info in event_helper.get_summary_salessegment_group(event):
            <%
                end = ""
                if sales_info['end']:
                    end = str(sales_info['end'].year) + "/" + str(sales_info['end'].month) + "/" + str(sales_info['end'].day)
                endif
            %>
            ${sales_info['group_name']}:${sales_info['start'].year}/${sales_info['start'].month}/${sales_info['start'].day}〜${end}
            <br />
        % endfor
    % else:
        ${event.deal_open.year}/${event.deal_open.month}/${event.deal_open.day}〜${event.deal_close.year}/${event.deal_close.month}/${event.deal_close.day}
    % endif
% endif
<div align="center">
    % if len(perfs):
        % if event.deal_close < get_now(request):
  <a href="#list">公演一覧</a><br />
　<font color="red">このイベントの販売は終了しました</font><br/>
        % else:
  &gt;&gt;<a href="#list">購入はこちらから</a>&lt;&lt;<br />
        % endif
    % endif
</div><br />

% if info['performers']:
    <%m:header>出演者</%m:header>
    ${helper.nl2br(info['performers'])|n}<br/>
    <br/>
% endif

% if info['notice']:
<%m:header>詳細/注意事項</%m:header>
<div>
    <font size="-1">
        ${helper.nl2br(info['notice'])|n}
    </font>
</div>
<br/>
% endif

% if info['ticket_payment']:
    <%m:header>お支払い方法</%m:header>
    ${helper.nl2br(info['ticket_payment'])|n}<br/>
    <br/>
% endif

% if info['ticket_pickup']:
    <%m:header>チケット引き取り方法</%m:header>
    ${helper.nl2br(info['ticket_pickup'])|n}<br/>
    <br/>
% endif

% if info['content']:
<%m:header>お問い合わせ</%m:header>
${helper.nl2br(info['content'])|n}
<br /><br />
% endif

<% text = self.template.get_def('render_info').render(event=event, helper=helper) %>
<%def name="render_info(event)">

</%def>
% if text:
<%m:band>公演詳細</%m:band>
<div>${text|n}</div>
% endif
<a name="list"></a>
<%def name="month_list(month_unit_keys, selected)">
% if len(month_unit_keys) >= 2:
<% last_year = None %>
% for year_month in month_unit_keys:
<% year, month = year_month.split('/') %>
% if year != last_year:
  % if last_year:
    <br />
  % endif
  ${year}年:
  <% first = True %>
% endif
% if selected != year_month:
  <a href="#${year_month}">${month}月</a>
% else:
  ${month}月
% endif
<% last_year = year; first = False %>
% endfor
<br />
% endif
</%def>
<%m:band>公演一覧</%m:band>
% if not len(perfs):
    現在、販売中の公演はありません。
% endif
<div>
  <% index = 0 %>
    % for count in range(len(month_unit_keys)):
        <% month = month_unit_keys[count] %>
        <% prev_month = month_unit_keys[count - 1] if count > 0 else None %>
        <% next_month = month_unit_keys[count + 1] if count + 1 < len(month_unit_keys) else None %>
        <a name="${month}" id="${month}"></a>
        <%m:line width="2" />
        <%m:header>${month}
        % if next_month:
           <a href="#${next_month}">▼</a>
        % endif
        % if prev_month:
           <a href="#${prev_month}">▲</a>
        % endif
        </%m:header>
        ${month_list(month_unit_keys, month)}
        <%m:line width="2" />
        <% first = True %>
        % for i, perf in enumerate(perfs):
            % if (str(perf['perf'].start_on.year) + "/" + str(perf['perf'].start_on.month).zfill(2) == month):
                <% index += 1 %>
                <%
                    start_on_candidates = [salessegment.start_on for salessegment in perf['perf'].sales if salessegment.publicp and salessegment.group.publicp]
                    end_on_candidates = [salessegment.end_on for salessegment in perf['perf'].sales if salessegment.end_on and salessegment.publicp and salessegment.group.publicp]
                %>
                % if not first:
                    <hr />
                % endif
                % if event.deal_close <  get_now(request) or not start_on_candidates:
                [${index}]<font size="-1">${perf['perf'].title}</font><br />
                % else:
                [${index}]<font size="-1"><a href="${purchase_links[perf['perf'].id]}">${perf['perf'].title}</a></font><br />
                % endif
                % if perf['perf'].open_on:
                    開場:${str(perf['perf'].open_on.year)[2:]}/${str(perf['perf'].open_on.month).zfill(2)}/${str(perf['perf'].open_on.day).zfill(2)}(${week[perf['perf'].open_on.weekday()]})
                    ${str(perf['perf'].open_on.hour).zfill(2)}:${str(perf['perf'].open_on.minute).zfill(2)}<br />
                % endif
                % if perf['perf'].start_on:
                    開演:${str(perf['perf'].start_on.year)[2:]}/${str(perf['perf'].start_on.month).zfill(2)}/${str(perf['perf'].start_on.day).zfill(2)}(${week[perf['perf'].start_on.weekday()]})
                    ${str(perf['perf'].start_on.hour).zfill(2)}:${str(perf['perf'].start_on.minute).zfill(2)}<br />
                % endif
                % if perf['perf'].venue:
                    会場:${perf['perf'].venue}<br/>
                % endif
                % if not start_on_candidates:
                    準備中
                %elif min(start_on_candidates) >= get_now(request):
                    販売前
                %elif not end_on_candidates:
                    % if not perf['perf'].purchase_link and perf['perf'].backend_id is None:
                        <div class="actions">
                            準備中
                        </div>
                    % elif not perf['perf'].purchase_link and stock_status.scores.get(int(perf['perf'].backend_id),0) <= 0:
                        予定枚数終了
                    % else:
                        <div align="center">
                        <%m:band bgcolor="#ffcccc">
                        % if event.deal_close >= get_now(request):
                          <a href="${purchase_links[perf['perf'].id]}"><font color="#cc0000">この公演のチケットを購入</font></a>
                        % endif
                        </%m:band>
                        </div>
                    % endif
                %elif max(end_on_candidates) >= get_now(request):
                    % if not perf['perf'].purchase_link and perf['perf'].backend_id is None:
                        <div class="actions">
                            準備中
                        </div>
                    % elif not perf['perf'].purchase_link and stock_status.scores.get(int(perf['perf'].backend_id),0) <= 0:
                        予定枚数終了
                    % else:
                        <div align="center">
                        <%m:band bgcolor="#ffcccc">
                        % if event.deal_close >= get_now(request):
                          <a href="${purchase_links[perf['perf'].id]}"><font color="#cc0000">この公演のチケットを購入</font></a>
                        % endif
                        </%m:band>
                        </div>
                    % endif
                % else:
                    販売期間終了
                % endif
                <% first = False %>
            % endif
        % endfor
        <br />
    % endfor
</div>
