## gadgets ＝ ある程度まとまったhtmlの構成要素。
<%namespace file="altaircms:templates/front/ticketstar/gadgets.mako" name="gadgets"/>


## ヘッダーの検索フォーム.jsと連携している
<%def name="search_form_on_header(placeholder, query_id)">
	<form id="form1" name="form1" method="GET" action="${request.route_path("page_search_by_freeword")}">
		<input name="q" type="text" id="${query_id}" size="40" placeholder="${placeholder}" />
		<input name="imageField" type="image" id="imageField" src="/static/ticketstar/img/common/header_search_btn.gif" alt="検索" />
		<a href="${request.route_path("page_search_input")}">詳細検索</a>
	</form>
</%def>

<%def name="sidebar_genre_listing(sub_categories)">
  <h2 class="sidebar-heading">ジャンル一覧</h2>
  <div class="sideCategoryGenre">
	<ul>
		% for c in sub_categories:
		  <li><a href="${h.link.get_searchpage(request, kind="genre", value=c.name)}">${c.label}</a></li>
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
	  <li><a href="${h.link.get_searchpage(request, kind="area", value=en)}">${ja}</a></li>
	  % endfor
	</ul>
  </dd>
</%def>

<%def name="sidebar_deal_cond_listing()">
<%
from altairsite.search.forms import DealCondPartForm
%>
<dt>販売状態で絞込み</dt>
<dd>
  <ul>
    % for en,ja in DealCondPartForm.deal_cond_choices:
	  <li><a href="${h.link.get_searchpage(request, kind="deal_cond", value=en)}">${ja}</a></li>
    % endfor
  </ul>
</dd>
</%def>

<%def name="sidebar_deal_open_listing()">
	<dt>発売日・受付日で絞込み</dt>
	<dd>
		<ul>
			<li><a href="${h.link.get_searchpage(request, kind="deal_open", value=7) }">7日以内に受付・発売開始</a></li>
			<li><a href="${h.link.get_searchpage(request, kind="deal_open", value=14) }">14日以内に受付・発売開始</a></li>
			<li><a href="${h.link.get_searchpage(request, kind="deal_open", value=30) }">30日以内に受付・発売開始</a></li>
		</ul>
	</dd>
</%def>

<%def name="sidebar_event_open_listing()">
	<dt>公演日で絞込み</dt>
	<dd>
		<ul>
			<li><a href="${h.link.get_searchpage(request, kind="event_open", value=7) }">7日以内に公演</a></li>
			<li><a href="${h.link.get_searchpage(request, kind="event_open", value=14) }">14日以内に公演</a></li>
			<li><a href="${h.link.get_searchpage(request, kind="event_open", value=30) }">30日以内に公演</a></li>
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

<%def name="hotword_itemize_header()">
<%
from altairsite.front.api import get_current_hotwords
hotwords = get_current_hotwords(request)
%>
	<ul>
	    % for word in hotwords:
		  ## dangerous?
		  <li><a href="${request.route_path("page_search_by", kind="hotword", value=word.name)}">${word.name}</a></li>
		% endfor
	</ul>
</%def>

<%def name="top_side_searchform()">
<%
from altairsite.search.forms import TopPageSidebarSearchForm
form = TopPageSidebarSearchForm()
%>
		<div id="sideSearch">
			<h2><img src="/static/ticketstar/img/index/title_search.gif" alt="チケットを探す" width="246" height="36" /></h2>
			<ul>
				<li><a href="${h.link.get_searchpage(request, kind="deal_cond", value="early_firstcome")}"><img src="/static/ticketstar/img/index/btn_presale.gif" alt="先行抽選" width="222" height="28" /></a></li>
				<li><a href="${h.link.get_searchpage(request, kind="deal_cond", value="normal")}"><img src="/static/ticketstar/img/index/btn_release.gif" alt="一般発売" width="222" height="28" /></a></li>
				<li><a href="${h.link.get_searchpage(request, kind="deal_open", value=7)}"><img src="/static/ticketstar/img/index/btn_now.gif" alt="すぐ見たい" width="222" height="28" /></a></li>
				<li><a href="${request.route_path("page_search_by_freeword",_query=dict(q=u"お買い得"))}"><img src="/static/ticketstar/img/index/btn_best.gif" alt="お買い得チケット" width="222" height="28" /></a></li>
			</ul>
			<form id="form2" name="form2" method="GET" action="${request.route_path("page_search_by_multi")}">
				<dl>
					<dt><img src="/static/ticketstar/img/index/search_day.gif" alt="開催日" width="37" height="13" /></dt>
					<dd>
                       ${form.start_year}
                       ${form.start_month}
                       ${form.start_day}
						<br />
                       ${form.end_year}
                       ${form.end_month}
                       ${form.end_day}
					</dd>
					<dt><img src="/static/ticketstar/img/index/search_place.gif" alt="開催場所" width="52" height="13" /></dt>
					<dd>
                        ${form.area}
					</dd>
				</dl>
				<p><input name="imageField2" type="image" id="imageField2" src="/static/ticketstar/img/index/btn_search.gif" alt="日程・場所で探す" /></p>
			</form>
		</div>
</%def>
nn
