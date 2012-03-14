<%inherit file='../layout_2col.mako'/>

<div class="row" style="margin-bottom: 9px">
  <h2 class="span6">イベントのタイトル - ${event['title']} (ID: ${event['id']})</h2>
  <div class="span4">
    <a class="btn" href="${request.route_path("page_add", event_id=event['id'])}"><i class="icon-plus"> </i> ページ追加</a>
    <a class="btn" href=""><i class="icon-eye-open"> </i> Preview</a>
    <a class="btn" href=""><i class="icon-refresh"> </i> Sync</a>
  </div>
</div>

<div class="row">
  <div class="span5">
    <table class="table table-striped">
      <tr>
        <th class="span2">タイトル</th><td>${event['title']}</td>
      </tr>
      <tr>
        <th class="span2">サブタイトル</th><td>${event['subtitle']}</td>
      </tr>
      <tr>
        <th class="span2">概要</th><td>${event['description']}</td>
      </tr>
      <tr>
        <th>開催期間</th><td>${event['event_open']} - ${event['event_close']}</td>
      </tr>
      <tr>
        <th>販売期間</th><td>${event['deal_open']} - ${event['deal_close']}</td>
      </tr>
    </table>
  </div>
  <div class="span5">
    <table class="span5 table table-striped">
      <tr>
        <th class="span2">開催場所</th><td>${event['place']}</td>
      </tr>
      <tr>
        <th class="span2">問い合わせ先</th><td>${event['inquiry_for']}</td>
      </tr>
    </table>
  </div>
</div>

<hr/>
<h2>パフォーマンス</h2>
<div class="row">
  <div class="span5">
   <table>
	 <thead><tr><th>講演名</th><th>講演日時</th><th>場所</th></tr>
	 </thead>
	 <tbody>
	   %for p in performances:
	     <tr><td>${p.title}</td><td>${ p.start_on }</td><td>${ p.venue }</td></tr>
	   %endfor
	 </tbody>
   </table>
  </div>
</div>
<hr/>

<h2>配下のページ一覧</h2>

<table>
    <tbody>
        %for page in pages:
            <tr>
                <td>
                    <a href="${request.route_path('page_edit', event_id=event["id"], page_id=page.id)}">${page}</a>
                    <a href="/f/${page.url|n}" target="_blank">preview</a></td>
            </tr>
        %endfor
    </tbody>
</table>
