<%inherit file="base.mako" />
<% member_set = _context.member_sets[0] %>
<div class="main">

    <div class="login-area clearfix">
        <div class="login-box login-box-1">
            <dl>
                <dt class="login-name">会員の方はこちら</dt>
                <dd><a href="${_context.route_path('extauth.fanclub.entry')}" class="btn-login-buy">会員IDでログインする</a></dd>
            </dl>
        </div><!-- /login-box for guest-->
    </div><!-- /login-area-->
    <div class="login-area clearfix">
        <div class="login-box login-box-1">
            <dl>
                <dt>一般の方はこちら</dt>
                <dd>
                    <form action="${_context.route_path('extauth.login',_query=request.GET)}" method="POST">
                        <input type="submit" name="doGuestLoginAsGuest" class="btn-login-buy" value="購入する">
                        <input type="hidden" name="member_set" value="TX">
                        <input type="hidden" name="_" value="${request.session.get_csrf_token()}" />
                    </form>
                </dd>
                <dd>
                <ul>
                    <li><span style="color:red;font-size:90%;">「会員の方はこちら」から各会員への新規登録が可能です</span></li>
                </ul>
                </dd>
            </dl>
        </div><!-- /login-box for guest-->
    </div><!-- /login-area-->

    <dl class="login-note">
        <dt>注意事項</dt>
        <dd>
        <ul>
            <li>※ 会員ID・パスワードは半角でご入力ください。</li>
        </ul>
        </dd>
    </dl>
    <dl class="login-note">
        <dt>お問い合わせ</dt>
        <dd>
        <ul>
            <li>お手数ですが、<a href="mailto:tokairadio@tstar.jp">こちら</a>までお問い合わせください。</li>
        </ul>
        </dd>
    </dl>

</div><!--main-->
