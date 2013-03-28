<!DOCTYPE html>
<html>
<%include file="../common/_header.mako" args="title=u'楽天チケット[ヘルプ]'"/>
<body>

    <div style="background-image:url(/static/mobile/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffc0cb">■</font>ヘルプ</font></div>

    <div class="line" style="background:#FFFFFF"><img src="/static/mobile/clear.gif" alt="" width="1" height="1" /></div>

    <a href="/" accesskey="0">[0]戻る</a>
    <a href="/" accesskey="9">[9]トップへ</a>
    <br/><br/>


    <a href="/">トップ</a> >> ヘルプ

    <div class="line" style="background:#FFFFFF"><img src="/static/mobile/clear.gif" alt="" width="1" height="1" /></div>

    <div style="background-image:url(/static/mobile/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffbf00">■</font><a name="top">ヘルプ</a></font></div>

    <div class="line" style="background:#FFFFFF"><img src="/static/mobile/clear.gif" alt="" width="1" height="1" /></div>

    % if form.helps.data:
        % for help in form.helps.data:
            <a href="#${help.id}">
                ${helper.nl2br(help.title)|n}
            </a><br/><br/>
        % endfor

        <a href="#top">トップへ</a>

        % for count, help in enumerate(form.helps.data):
            <hr/>
            <a name="${help.id}" id="${help.id}">
                ${helper.nl2br(help.title)|n}<br/><br/>
            </a>
            ${helper.nl2br(help.text)|n}<br/>
            % if (count + 1) % 5 == 0 or len(form.helps.data) == count + 1:
                <hr/>
                <a href="#top">トップへ</a>
            % endif
        % endfor
    % endif

    <%include file="../common/_footer.mako" />
</body>
</html>