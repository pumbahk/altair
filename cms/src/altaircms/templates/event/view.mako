<%inherit file='../layout.mako'/>

<h1>イベントのタイトル - ${event.title} (ID: ${event.id})</h1>
<a href="">プレビュー（preview）</a> <a href="">バックから最新情報取得（sync）</a>

<hr/>

<a href="/event/${event.id}/page/edit">ページ追加</a>

<h2>イベント配下のページ一覧</h2>

<table>
    <tbody>
        %for page in pages:
            <tr>
                ## 編集を追加する
                <td>${page} 
                    <a href="${request.route_url('page_edit', event_id=event.id, page_id=page.id)}">edit</a>
                    <a href="/f/${page.url|n}" target="_blank">preview</a></td>
            </tr>
        %endfor
    </tbody>
</table>
