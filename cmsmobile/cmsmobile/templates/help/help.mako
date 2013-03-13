<!DOCTYPE html>
<html>
<%include file="../common/_header.mako" args="title=u'楽天チケット[ヘルプ]'"/>
<body>

<div style="font-size: x-small">
    <a href="/">トップ</a> >> ヘルプ
</div>

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;font-size: medium;
                        color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">ヘルプ</div>

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    % if form.helps.data:
        % for help in form.helps.data:
            <a href="#${help.id}">
                <div style="font-size: medium">Ｑ．${help.title}</div>
            </a>
        % endfor

        <div style="font-size: x-small"><a href="/">楽天チケットトップへ</a></div>

        % for count, help in enumerate(form.helps.data):
            % if count % 5 == 0 and count != 0:
                <hr/>
                <div style="font-size: x-small">
                    <a href="/">楽天チケットトップへ</a>
                </div>
            % endif
            <hr/>
            <a name="${help.id}" id="${help.id}">
                <div style="font-size: x-small">Ｑ．${help.title}</div>
            </a>
            Ａ．${help.text}<br/>
            ${count}
        % endfor

        % if (len(form.helps.data) + 1 ) % 5 != 0:
            <hr/>
            <a href="/"><span style="font-size: x-small">楽天チケットトップへ</span></a>
        % endif
    % endif

    <%include file="../common/_footer.mako" />
</body>
</html>