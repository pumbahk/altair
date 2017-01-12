<%inherit file="base.mako" />
<div class="main">

    <div class="login-area clearfix">
        <div class="login-box login-box-1">
            <dl>
                <dt class="login-name">ファンクラブ会員の方</dt>
                <dd><a href="${_context.route_path('extauth.fanclub.entry')}" class="btn-login">ファンクラブ会員IDでログイン</a></dd>
                <dd><a href="${_context.route_path('extauth.fanclub.entry')}" class="btn-regist" target="_blank">ファンクラブ会員に登録する</a></dd>
            </dl>
        </div><!-- /login-box-->
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
            <li>お手数ですが、<a href="mailto:satv@tstar.jp">こちら</a>までお問い合わせください。</li>
        </ul>
        </dd>
    </dl>

</div><!--main-->
