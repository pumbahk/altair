<!DOCTYPE html>
<html>
<%include file="../common/_header.mako" args="title=u'楽天チケット[ヘルプ]'"/>
<body>

    <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffc0cb">■</font>ヘルプ</font></div>

    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    <a href="/" accesskey="0">[0]戻る</a>
    <a href="/" accesskey="9">[9]トップへ</a>
    <br/><br/>


    <a href="/">トップ</a> >> ヘルプ

    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>ヘルプ</font></div>

    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    % if form.helps.data:
        % for help in form.helps.data:
            <a href="#${help.id}">
                Ｑ．${help.title}
            </a><br/><br/>
        % endfor

        <a href="/">トップへ</a>

        % for count, help in enumerate(form.helps.data):
            <hr/>
            <a name="${help.id}" id="${help.id}">
                Ｑ．${help.title}<br/>
            </a>
            Ａ．${help.text}<br/>
            % if (count + 1) % 5 == 0 or len(form.helps.data) == count + 1:
                <hr/>
                <a href="/">トップへ</a>
            % endif
        % endfor
    % endif

    <%include file="../common/_footer.mako" />
</body>
</html>