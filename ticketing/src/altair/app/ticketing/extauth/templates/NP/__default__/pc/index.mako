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
            <li>会員の方も、受付番号から確認することができます。</li>
            <li>会員ID・パスワードは半角でご入力ください。</li>
        </ul>
        </dd>
    </dl>
    <dl class="login-note">
        <dt>お問い合わせ</dt>
        <dd>
        <ul>
            <li>チケットスター TEL: 000-0000-0000（平日10時～18時）※不定休</li>
        </ul>
        </dd>
    </dl>

</div><!--main-->
