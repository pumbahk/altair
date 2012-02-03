<%inherit file="layout.mako" />
<%block name="title">管理画面トップ</%block>
<ul>
  <li>
    <a href="${request.route_path('admin.events.top')}">イベント管理</a>
    <ul>
      <li><a href="${request.route_path('admin.events.list')}">イベント一覧</a></li>
      <li><a href="${request.route_path('admin.events.new')}">イベント編集 / 新規登録</a></li>
      <li>
        <a href="${request.route_path('admin.events.show', event_id=1)}">イベント詳細表示</a>
        <ul>
          <li>
            パフォーマンス編集
            <ul>
              <li><a href="${request.route_path('admin.performances.new', event_id=1, performance_id=1)}">パフォーマンス編集 / 新規登録</a></li>
            </ul>
          </li>
        </ul>
      </li>
      <li><a href="${request.route_path('admin.events.top')}">レポート送信</a></li>
    </ul>
  </li>
  <li>
    <a href="${request.route_path('admin.users.top')}">ユーザ管理</a>
    <ul>
      <li><a href="${request.route_path('admin.users.list')}">ユーザ一覧</a></li>
      <li><a href="${request.route_path('admin.users.new')}">ユーザ編集 / 新規登録</a></li>
      <li><a href="${request.route_path('admin.users.show', user_id=1)}">ユーザ詳細</a></li>
    </ul>
  </li>
  <li>
    <a href="${request.route_path('admin.purchasables.top')}">商品管理</a>
    <ul>
      <li><a href="${request.route_path('admin.purchasables.list')}">商品一覧</a></li>
      <li><a href="${request.route_path('admin.purchasables.new')}">商品新規登録 / 編集</a></li>
      <li><a href="${request.route_path('admin.purchasables.show', id=1)}">商品詳細</a></li>
    </ul>
  </li>
  <li>
    <a href="${request.route_path('admin.masterdata.top')}">マスタ登録</a>
    <ul>
      <li>
        <a href="${request.route_path('admin.payment_methods.top')}">支払方法マスタ登録</a>
        <ul>
          <li><a href="${request.route_path('admin.payment_methods.list')}">支払方法マスタ一覧</a></li>
          <li><a href="${request.route_path('admin.payment_methods.new')}">支払方法マスタ新規登録 / 編集</a></li>
        </ul>
      </li>
      <li>
        <a href="${request.route_path('admin.delivery_methods.top')}">配送方法マスタ登録</a>
        <ul>
          <li><a href="${request.route_path('admin.delivery_methods.list')}">配送方法マスタ一覧</a></li>
          <li><a href="${request.route_path('admin.delivery_methods.new')}">配送方法マスタ新規登録 / 編集</a></li>
        </ul>
      </li>
      <li>
        <a href="${request.route_path('admin.payment_delivery_method_pairs.top')}">支払配送方法マスタ登録</a>
        <ul>
          <li><a href="${request.route_path('admin.payment_delivery_method_pairs.list')}">支払配送方法マスタ一覧</a></li>
          <li><a href="${request.route_path('admin.payment_delivery_method_pairs.new')}">支払配送方法マスタ新規登録 / 編集</a></li>
        </ul>
      </li>
      <li>
        <a href="${request.route_path('admin.sites.top')}">会場マスタ登録</a>
        <ul>
          <li><a href="${request.route_path('admin.sites.list')}">会場マスタ一覧</a></li>
          <li><a href="${request.route_path('admin.sites.new')}">会場マスタ新規登録 / 編集</a></li>
        </ul>
      </li>
      <li>
        <a href="${request.route_path('admin.performer.top')}">パフォーマー管理</a>
        <ul>
          <li><a href="${request.route_path('admin.performer.list')}">パフォーマー一覧</a></li>
          <li><a href="${request.route_path('admin.performer.new')}">パフォーマー登録 / 編集</a></li>
        </ul>
      </li>
    </ul>
  </li>
</ul>
