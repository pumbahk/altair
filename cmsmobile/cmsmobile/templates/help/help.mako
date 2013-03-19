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
            </a>
        % endfor

        <a href="/">楽天チケットトップへ</a>

        % for count, help in enumerate(form.helps.data):
            % if count % 5 == 0 and count != 0:
                <hr/>
                    <a href="/">楽天チケットトップへ</a>
            % endif
            <hr/>
            <a name="${help.id}" id="${help.id}">
                Ｑ．${help.title}
            </a>
            Ａ．${help.text}<br/>
            ${count}
        % endfor

        % if (len(form.helps.data) + 1 ) % 5 != 0:
            <hr/>
            <a href="/">楽天チケットトップへ</a>
        % endif
    % endif

    <%include file="../common/_footer.mako" />
</body>
</html>