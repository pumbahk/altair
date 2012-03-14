<%inherit file='layout.mako'/>

<div class="row">
    <div class="span6 offset3 well"  style="text-align:center" >
        <a class="btn btn-primary" href="${request.route_url("oauth_entry")}">Login with Twitter (OAuth)</a>
    </div>
</div>

<%doc>
<form action="${url}" method="post">
    <input type="hidden" name="came_from" value="${came_from}"/>
    <input type="text" name="login" value="${login}"/><br/>
    <input type="password" name="password"
           value="${password}"/><br/>
    <input type="submit" name="form.submitted" value="Log In"/>
</form>

<form action="https://api.id.rakuten.co.jp/openid/auth" method="get">
    <input type="hidden" name="openid.ns" value="http://specs.openid.net/auth/2.0"/>
    <input type="hidden" name="end_point" value="https://127.0.0.1:6543/rakuten/openid/auth"/>
    <input type="hidden" name="openid.return_to" value="https://127.0.0.1:6543/rakuten/openid/auth"/>
    <input type="hidden" name="openid.claimed_id" value="http://specs.openid.net/auth/2.0/identifier_select"/>
    <input type="hidden" name="openid.identity" value="http://specs.openid.net/auth/2.0/identifier_select"/>
    <input type="hidden" name="openid.mode" value="checkid_setup"/>
    <input type="hidden" name="openid.ns.oauth" value="http://specs.openid.net/extenstions/oauth/1.0"/>
    <input type="hidden" name="openid.oauth.consumer" value=""/>
    <input type="hidden" name="openid.oauth.scope" value=""/>
    <input type="text" name="openid_identifier"/>
    <input type="submit" value="Login with OpenID"/>
</form>

<form action="/oauth/google/auth" method="post">
    <input type="hidden" name="popup_mode" value="popup">
    <input type="hidden" name="end_point" value="http://127.0.0.1:6543/login">
    <input type="submit" value="Login with Google">
</form>
</%doc>
