<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/html">
    <%include file="../common/_header.mako" args="title=u'公演中止情報'"/>
<body>

    <div style="font-size: x-small">
        <a href="/">トップ</a> >> 公演中止・変更情報
    </div>
    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;font-size: medium;
                        color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">公演中止・変更情報</div>

    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

        % if form.informations.data:
        % for info in form.informations.data[0:10]:
            <hr/>
            <div style="font-size: x-small">公演：${info.title}</div>
            <span style="font-size: x-small">詳細：${info.text}</span>
        % endfor

        % if len(form.informations.data) > 10:
            <hr/>
            <a href="/infodetail"><span style="font-size: x-small">すべてを見る</span></a>
        % endif
    % else:
        <span style="font-size: x-small">公演中止情報はありません。</span>
    % endif
    <%include file="../common/_footer.mako" />
</body>
</html>
