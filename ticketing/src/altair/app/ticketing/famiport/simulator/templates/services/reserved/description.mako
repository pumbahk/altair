<%inherit file="/_base.mako" />
<h1>サービス説明</h1>
<div>
  <p>${_context.client.name}の説明です</p>
  <a href="${request.route_path('service.reserved.info1')}">次へ</a>
</div>
