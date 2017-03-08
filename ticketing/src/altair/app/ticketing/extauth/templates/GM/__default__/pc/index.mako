<%inherit file="base.mako" />
<% member_set = _context.member_sets[0] %>
<div class="main">

    <div class="login-area clearfix">
        <div class="login-box login-box-1">
            <dl>
                <dt>会員の方はこちら</dt>
                <dd><a href="${_context.route_path('extauth.fanclub.entry')}" class="btn-login-buy">会員IDでログインする</a></dd>
                <dd>
                </dd>
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
                        <input type="hidden" name="member_set" value="GM">
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

    <!--
        <div class="login-box login-box-2">
            <dl>
              <dt>クーポンをお持ちの方はこちら</dt>
              <dd>
                  <form action="${_context.route_path('extauth.login')}" method="POST">
                      <table class="table-login">
                        <tbody>
                        <tr>
                            <th>ログインID</th>
                            <td><input type="text" class="text" name="username" value="" /></td>
                        </tr>
                        <tr>
                            <th>パスワード</th>
                            <td><input type="password" name="password" value="" /></td>
                        </tr>
                        </tbody>
                      </table>
                      <input type="hidden" name="member_set" value="${member_set.name}" />
                      <input type="hidden" name="_" value="${request.session.get_csrf_token()}" />
                      ${message if message else ""}
                      <button type="submit" class="btn-login">ログインする</button>
                  </form>
              </dd>
            </dl>
        </div>
    -->

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
