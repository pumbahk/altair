<%inherit file="/base.mako" />

<style type="text/css">
    .error-msg-wrap {
        display: block;
        margin: 20px auto;
        width: 600px;
    }
    .error-msg-wrap ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .error-msg-wrap ul li {
        font-size: 16px;
        font-weight: bold;
        color: #CF0000;
    }
    #login-form {
        margin-top: 30px;
        margin-bottom: 16px;
    }
    .spacer {
        width: 100px;
        margin: 0 auto;
    }
</style>
<%
    msgs = request.session.pop_flash()
%>
% if msgs:
<div class="error-msg-wrap">
<ul>
    % for msg in msgs:
    <li>${msg}</li>
    % endfor
</ul>
</div>
% endif
<div class="container" style="width: 600px;">
    <div class="page-header">
    <h1>ログ  イン</h1>
    </div>

    <div class="well">
        <form id="login-form" class="form-horizontal" action="${request.current_route_path(_query=request.GET)}" method="POST">
            <fieldset>
                <div class="control-group">
                    <label for="${form.user_name.id}" class="control-label">ユーザ名</label>
                    <div class="controls">${form.user_name()}</div>
                </div>
                <div class="control-group">
                    <label for="${form.password.id}" class="control-label">パスワード</label>
                    <div class="controls">${form.password()}</div>
                </div>
            </fieldset>
            <div class="spacer">
                <input class="btn btn-primary" type="submit" name="submit" value="ログイン">
            </div>
        </form>
    </div>
</div>

