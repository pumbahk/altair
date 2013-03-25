<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/html">
    <%include file="../common/_header.mako" args="title=u'公演中止情報'"/>
<body>

    <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffc0cb">■</font>公演中止・変更情報</font></div>

    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    <a href="/" accesskey="0">[0]戻る</a>
    <a href="/" accesskey="9">[9]トップへ</a>
    <br/><br/>

        <a href="/">トップ</a> >> 公演中止・変更情報

    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>公演中止・変更情報</font></div>

    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    % if form.informations.data:
        % for count, info in enumerate(form.informations.data[0:10]):
            % if count > 0:
                <hr/>
            % endif
            公演：${helper.nl2br(info.title)|n}<br/>
            詳細：${helper.nl2br(info.text)|n}<br/>
        % endfor

        % if len(form.informations.data) > 10:
            <hr/>
            <a href="/infodetail">すべてを見る</a>
        % endif
    % else:
        公演中止・変更情報はありません。
    % endif
    <%include file="../common/_footer.mako" />
</body>
</html>
