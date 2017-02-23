<%inherit file="base.mako" />
<div class="main">

    <div class="login-area clearfix">
        <div class="login-box login-box-2">
            <dl>
                <dt class="login-name">会員の方はこちら</dt>
                % if oauth_service_providers:
                % for provider in oauth_service_providers:
                <dd><a href="${_context.route_path('extauth.fanclub.entry', _query=dict(service_provider_name=provider.name))}" class="btn-login">${provider.display_name}<span style="font-size:80%">でログイン</span></a></dd>
                % endfor
                % endif
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
                        <br/><br/>
                        <a href="https://parceiro.tstar.jp/cart/events/9657">
                            <input type="button" class="btn-regist" value="サポーターズクラブへの新規入会はこちら">
                        </a>
                        <input type="hidden" name="member_set" value="NP">
                        <input type="hidden" name="_" value="${request.session.get_csrf_token()}" />
                    </form>
                </dd>
                <dd>
                <ul>
                    <li><span style="color:red;font-size:90%;">※現在、下記からのご入会は受け付けておりません。</span></li>
                    <li><img src="${view_context.static_url('images/fc_login_capture.png')}" alt="logo" width="85%" /></li>
                </ul>
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
            <li>お手数ですが、<a href="mailto:parceiro@tstar.jp">こちら</a>までお問い合わせください。</li>
        </ul>
        </dd>
    </dl>

</div><!--main-->
