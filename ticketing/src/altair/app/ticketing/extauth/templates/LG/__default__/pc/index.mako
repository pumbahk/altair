<%inherit file="base.mako" />

<div class="main">

    <div class="login-area clearfix">
        <div class="login-box login-box-2">
            <dl>
                <dt class="login-name">会員の方はこちら</dt>
                <dd><a href="${_context.route_path('extauth.fanclub.entry')}" class="btn-login">会員IDでログイン</a></dd>
                <dd><a href="${_context.route_path('extauth.fanclub.entry')}" class="btn-regist" target="_blank">会員登録する</a></dd>
                <dd>
                <ul>
                    <li>※ 会員ID・パスワードは半角でご入力ください。</li>
                </ul>
                </dd>
            </dl>
        </div><!-- /login-box-->
        <div class="login-box login-box-2">
            <dl>
                <dt>一般の方はこちら</dt>
                <dd>
                    <form action="${_context.route_path('extauth.login',_query=request.GET)}" method="POST">
                        <input type="submit" name="doGuestLoginAsGuest" class="btn-login" value="購入する">
                        <input type="hidden" name="member_set" value="LG">
                        <input type="hidden" name="_" value="${request.session.get_csrf_token()}" />
                    </form>
                </dd>
            </dl>
        </div>
    </div><!-- /login-area-->

    <dl class="login-note">
        <dt>ご購入前にご確認ください！</dt>
        <dd>
        <ul>
            <li><span style="font-weight: bold;">@tstar.jp / @ticketstar.jp</span>からのメールが受け取れるよう設定してください。お客様ご自身でドメイン指定の設定をお願い致します。（お持ちの<span style="font-weight: bold;">PC・スマートフォン</span>の設定をご確認ください）</li>
        </ul>
        </dd>
    </dl>
    <dl class="login-note">
        <dt>お問い合わせ</dt>
        <dd>
        <ul>
            <li>お手数ですが、<a href="mailto:lagunatenbosch@tstar.jp">こちら</a>までお問い合わせください。</li>
        </ul>
        </dd>
    </dl>

</div><!--main-->
