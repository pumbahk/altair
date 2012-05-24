<%inherit file="altaircms:templates/front/ticketstar/search/detail_search_result.mako"/>
<%namespace file="altaircms:templates/front/ticketstar/gadgets.mako" name="gadgets"/>

<%block name="main">

	  <h3>検索条件:</h3>
      <div id="searchQuery">
		## 検索条件指定(intersection,union)？
		${query_params}
	  </div>

	<h2><img src="/static/ticketstar/img/search/title_results.gif" alt="チケット検索結果" width="742" height="43" /></h2>

	% if not result_seq:
	  <div class="search-message">
		<h3>該当するチケットはありません</h3>
		<p class="message">他の検索条件で再度検索してみてください</p>
		${gadgets.search_form_on_header(u"アーティスト名、公演名、会場名など")}
	  </div>
	% else:

	  <%
seq = h.paginate(request, result_seq, items_per_page=10, item_count=len(result_seq))
current_items_count = seq.page * seq.items_per_page
%>
	  <div id="paginateInfo">
		<p class="align1">
		  全 ${seq.item_count }件中
		  ${max(1,current_items_count - seq.items_per_page)}〜${min(current_items_count,seq.item_count)}件を表示中
		</p>
	  </div>

	  ${seq.pager(format=u"$link_first $link_previous 前を表示 ~3~ 次を表示 $link_next $link_last ")}

	  % for result in seq.paginated():
		${result}
	  % endfor

	  ${seq.pager(format=u"$link_first $link_previous 前を表示 ~3~ 次を表示 $link_next $link_last ")}
    % endif
</%block>

<%block name="side">
  <!-- InstanceBeginEditable name="side" -->
  <div class="sideCategoryGenre">
	<h2>カテゴリー一覧</h2>
	<ul>
	  <li><a href="#">音楽</a></li>
	  <li><a href="#">演劇</a></li>
	  <li><a href="#">スポーツ</a></li>
	  <li><a href="#">イベント・その他</a></li>
	</ul>
  </div>

  <dl id="sideRefineSearch">
	<dt>エリアを選択</dt>
	<dd>
	  <ul>
		<li><a href="#">北海道</a></li>
		<li><a href="#">東北</a></li>
		<li><a href="#">関東甲信越</a></li>
		<li><a href="#">中部</a></li>
		<li><a href="#">北陸</a></li>
		<li><a href="#">関西</a></li>
		<li><a href="#">中国・四国</a></li>
		<li><a href="#">九州・沖縄</a></li>
	  </ul>
	</dd>
	<dt>販売状態で絞込み</dt>
	<dd>
	  <ul>
		<li><a href="#">最速抽選</a></li>
		<li><a href="#">先行抽選</a></li>
		<li><a href="#">先行先着</a></li>
		<li><a href="#">一般発売</a></li>
		<li><a href="#">追加抽選</a></li>
	  </ul>
	</dd>
	<dt>発売日・受付日で絞込み</dt>
	<dd>
	  <ul>
		<li><a href="#">7日以内に受付・発売開始</a></li>
		<li><a href="#">14日以内に受付・発売開始</a></li>
		<li><a href="#">30日以内に受付・発売開始</a></li>
	  </ul>
	</dd>
	<dt>公演日で絞込み</dt>
	<dd>
	  <ul>
		<li><a href="#">7日以内に公演</a></li>
		<li><a href="#">14日以内に公演</a></li>
		<li><a href="#">30日以内に公演</a></li>
	  </ul>
	</dd>
  </dl>
  <dl id="sideInfo">
	<dt><img src="/static/ticketstar/img/common/side_info_title.gif" alt="お知らせ" width="190" height="18" /></dt>
	<dd>
	  <ul>
		<li>2011年12月4日(日)　～　2011年12月4日(日)　メンテナンスを行います</li>
		<li>2011年12月4日(日)　～　2011年12月4日(日)　メンテナンスを行います</li>
	  </ul>
	</dd>
  </dl>
  <!-- InstanceEndEditable -->
  <ul id="sideBtn">
	<li><a href="#"><img src="/static/ticketstar/img/mypage/btn_use.gif" alt="楽天チケットの使い方" width="202" height="28" /></a></li>
	<li><a href="#"><img src="/static/ticketstar/img/mypage/btn_favorite.gif" alt="お気に入りアーティストを登録" width="202" height="28" /></a></li>
	<li><a href="#"><img src="/static/ticketstar/img/mypage/btn_magazine.gif" alt="メルマガの購読" width="202" height="28" /></a></li>
  </ul>
</%block>
