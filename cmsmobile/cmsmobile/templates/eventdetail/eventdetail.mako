<%include file="../common/_header.mako" args="title=u'イベント詳細'"/>
<body>

<a href="/">トップ</a> >> イベント詳細<p/>

<h2>
    ${event.title}<br/>
</h2>

    公演期間：${event.deal_open}〜${event.deal_close}<br/>
    公演一覧へ<br/>
        2013/04｜2013/05｜2013/06<br/>
    <a href="#detail">公演詳細へ</a><br/>
<hr/>
<h3>公演一覧</h3>
    2013/04<br/>
    % for perf in event.performances:
        開場：${perf.open_on} 開演：${perf.start_on} 会場：${perf.venue}<br/>
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
