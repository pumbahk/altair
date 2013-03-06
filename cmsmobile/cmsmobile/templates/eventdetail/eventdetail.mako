<%include file="../common/_header.mako" args="title=u'イベント詳細'"/>
<body>

<a href="/">トップ</a> >> イベント詳細<p/>

<%
    week = {0:u'月',1:u'火',2:u'水',3:u'木',4:u'金',5:u'土',6:u'日'}
%>
<h2>
    ${event.title}<br/>
</h2>

    公演期間：${event.deal_open.year}/${event.deal_open.month}/${event.deal_open.day}(${week[event.deal_open.weekday()]})〜${event.deal_close.year}/${event.deal_close.month}/${event.deal_close.day}(${week[event.deal_close.weekday()]})<br/>
    公演一覧へ<br/>
        2013/04｜2013/05｜2013/06<br/>
    <a href="#detail">公演詳細へ</a><br/>
<hr/>
<h3>公演一覧</h3>
    2013/04<br/>
    % for perf in event.performances:
        開場:${str(perf.open_on.year)[2:]}/${perf.open_on.month}/${perf.open_on.day}
        開演:${str(perf.start_on.year)[2:]}/${perf.start_on.month}/${perf.start_on.day}
        会場:${perf.venue}<br/>
    % endfor
<hr/>
<h3><a name="detail">公演詳細</a></h3>
    販売キャンセル<br/>
    詳細/注意事項<br/>
    席種/価格<br/>
    お問合せ<br/>
        XX-XXXX-XXXX
    <%include file="../common/_footer.mako" />
</body>
</html>
