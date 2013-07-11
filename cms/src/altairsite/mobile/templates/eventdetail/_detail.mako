<%namespace file="../common/tags_mobile.mako" name="m" />
<%page args="event, week, month_unit, month_unit_keys, purchase_links, tickets, sales_start, sales_end, helper" />
<%
    perfs = []
    for perf in event.performances:
        if perf.public:
            perfs.append({"perf":perf, "display_order":perf.display_order})
    perfs = sorted(perfs, key=lambda v: (v['display_order']))
%>

<%m:header>公演期間</%m:header>
<% from altaircms.datelib import get_now %>
${event.event_open.year}/${str(event.event_open.month).zfill(2)}/${str(event.event_open.day).zfill(2)}(${week[event.event_open.weekday()]})〜${event.event_close.year}/${str(event.event_close.month).zfill(2)}/${str(event.event_close.day).zfill(2)}(${week[event.event_close.weekday()]})<br/>
<%m:header>販売期間</%m:header>
% if event.salessegment_groups:
    % for segment in event.salessegment_groups:
        % if segment.publicp:
            ${segment.name}:${segment.start_on.year}/${segment.start_on.month}/${segment.start_on.day}〜${segment.end_on.year}/${segment.end_on.month}/${segment.end_on.day}
            <br/>
        % endif
    % endfor
    <br />
% else:
    ${event.deal_open.year}/${event.deal_open.month}/${event.deal_open.day}〜${event.deal_close.year}/${event.deal_close.month}/${event.deal_close.day}
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
<% text = self.template.get_def('render_info').render(event=event, helper=helper) %>
<%def name="render_info(event)">
% if event.notice:
<%m:header>詳細/注意事項</%m:header>
<div><font size="-1">
${helper.nl2br(event.notice)|n}
</font></div>
<br/><br/>
% endif
% if event.inquiry_for:
<%m:header>お問い合わせ</%m:header>
${helper.nl2br(event.inquiry_for)|n}
<br /><br />
% endif
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
% if event.id == 211 or event.id == 219:
        <%m:line width="2" />
        <%m:header>
          楽天オープン
        </%m:header>
        <%m:line width="2" />
        <% first = True %>
        % for i, perf in enumerate(perfs):
            <% index += 1 %>
            <%
                start_on_candidates = [salessegment.start_on for salessegment in perf['perf'].sales]
                end_on_candidates = [salessegment.end_on for salessegment in perf['perf'].sales if salessegment.end_on]
            %>
            % if not first:
                <hr />
            % endif
            % if event.deal_close <  get_now(request):
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
            %elif max(end_on_candidates) >= get_now(request):
                <div align="center">
                <%m:band bgcolor="#ffcccc">
                % if event.deal_close >= get_now(request):
                  <a href="${purchase_links[perf['perf'].id]}"><font color="#cc0000">この公演のチケットを購入</font></a>
                % endif
                </%m:band>
                </div>
            % else:
                販売期間終了
            % endif
            <% first = False %>
        % endfor
        <br />
% else:
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
        % for i, perf in enumerate(event.performances):
            % if (str(perf.start_on.year) + "/" + str(perf.start_on.month).zfill(2) == month) and perf.public:
                <% index += 1 %>
                <%
                    start_on_candidates = [salessegment.start_on for salessegment in perf.sales]
                    end_on_candidates = [salessegment.end_on for salessegment in perf.sales if salessegment.end_on]
                %>
                % if not first:
                    <hr />
                % endif
                % if event.deal_close <  get_now(request) or not start_on_candidates:
                [${index}]<font size="-1">${perf.title}</font><br />
                % else:
                [${index}]<font size="-1"><a href="${purchase_links[perf.id]}">${perf.title}</a></font><br />
                % endif
                % if perf.open_on:
                    開場:${str(perf.open_on.year)[2:]}/${str(perf.open_on.month).zfill(2)}/${str(perf.open_on.day).zfill(2)}(${week[perf.open_on.weekday()]})
                    ${str(perf.open_on.hour).zfill(2)}:${str(perf.open_on.minute).zfill(2)}<br />
                % endif
                % if perf.start_on:
                    開演:${str(perf.start_on.year)[2:]}/${str(perf.start_on.month).zfill(2)}/${str(perf.start_on.day).zfill(2)}(${week[perf.start_on.weekday()]})
                    ${str(perf.start_on.hour).zfill(2)}:${str(perf.start_on.minute).zfill(2)}<br />
                % endif
                % if perf.venue:
                    会場:${perf.venue}<br/>
                % endif
                % if not start_on_candidates:
                    準備中
                %elif min(start_on_candidates) >= get_now(request):
                    販売前
                %elif max(end_on_candidates) >= get_now(request):
                    <div align="center">
                    <%m:band bgcolor="#ffcccc">
                    % if event.deal_close >= get_now(request):
                      <a href="${purchase_links[perf.id]}"><font color="#cc0000">この公演のチケットを購入</font></a>
                    % endif
                    </%m:band>
                    </div>
                % else:
                    販売期間終了
                % endif
                <% first = False %>
            % endif
        % endfor
        <br />
    % endfor
% endif
</div>
