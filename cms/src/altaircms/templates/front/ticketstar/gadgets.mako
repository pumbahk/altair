## gadgets ＝ ある程度まとまったhtmlの構成要素。
<%namespace file="altaircms:templates/front/ticketstar/gadgets.mako" name="gadgets"/>


## ヘッダーの検索フォーム.jsと連携している
<%def name="search_form_on_header(placeholder)">
	<form id="form1" name="form1" method="GET" action="${request.route_path("page_search_by")}">
		<input name="textfield" type="text" id="textfield" size="40" value="${placeholder}" onblur="if(this.value=='') this.value='${placeholder}';" onfocus="if(this.value=='${placeholder}') this.value='';" />
		<input name="imageField" type="image" id="imageField" src="/static/ticketstar/img/common/header_search_btn.gif" alt="検索" />
		<a href="${request.route_path("page_search_input")}">詳細検索</a>
	</form>
</%def>

<%def name="sidebar_genre_listing(sub_categories)">
  <div class="sideCategoryGenre">
	<h2>ジャンル一覧</h2>
	<ul>
		% for c in sub_categories:
		  <li><a href="${h.link.get_searchpage_from_category(request, c, kind="genre", _query={c.name: "on"})}">${c.label}</a></li>
		% endfor
	</ul>
  </div>
</%def>

<%def name="sidebar_area_listing(areas)">
<%
from altaircms.seeds.area import AREA_CHOICES
%>
			<dt>エリアを選択</dt>
			<dd>
				<ul>
				    % for en,ja in AREA_CHOICES:
					  <li><a href="#">${ja}</a></li>
					  ##<li><a href="${h.link.get_seachpage(request, kind="area", _query={en: ""}}">${ja}</a></li>
					% endfor
				</ul>
			</dd>
</%def>

<%def name="sidebar_deal_cond_listing()">
		  dummy
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
</%def>
<%def name="sidebar_deal_term_listing()">
		  dummy
			<dt>発売日・受付日で絞込み</dt>
			<dd>
				<ul>
					<li><a href="#">7日以内に受付・発売開始</a></li>
					<li><a href="#">14日以内に受付・発売開始</a></li>
					<li><a href="#">30日以内に受付・発売開始</a></li>
				</ul>
			</dd>
</%def>
<%def name="sidebar_performance_term_listing()">
		  dummy
			<dt>公演日で絞込み</dt>
			<dd>
				<ul>
					<li><a href="#">7日以内に公演</a></li>
					<li><a href="#">14日以内に公演</a></li>
					<li><a href="#">30日以内に公演</a></li>
				</ul>
			</dd>
</%def>

<%def name="sidebar_maintenance()">
		<dl id="sideInfo">
			<dt><img src="../img/common/side_info_title.gif" alt="お知らせ" width="190" height="18" /></dt>
			<dd>
				<ul>
					<li>2011年12月4日(日)　～　2011年12月4日(日)　メンテナンスを行います</li>
					<li>2011年12月4日(日)　～　2011年12月4日(日)　メンテナンスを行います</li>
				</ul>
			</dd>
		</dl>
</%def>

<%def name="sidebar_sideBtn()">
		<ul id="sideBtn">
			<li><a href="#"><img src="/static/ticketstar/img/mypage/btn_use.gif" alt="楽天チケットの使い方" width="202" height="28" /></a></li>
			<li><a href="#"><img src="/static/ticketstar/img/mypage/btn_favorite.gif" alt="お気に入りアーティストを登録" width="202" height="28" /></a></li>
			<li><a href="#"><img src="/static/ticketstar/img/mypage/btn_magazine.gif" alt="メルマガの購読" width="202" height="28" /></a></li>
		</ul>
</%def>

<%def name="sidebar_category_listing(categories)">
  <div class="sideCategoryGenre">
	<h2>カテゴリー一覧</h2>
	<ul>
	  ## this is too-adhoc! depends on categories[0] == category-of-toppage
	  % for category in categories[1:]:
        <li><a href="${h.link.get_link_from_category(request, category)}" alt="${category.label}">${category.label}</a></li>
	  % endfor
	</ul>
  </div>
</%def>
