<%inherit file="altaircms:templates/front/ticketstar/search/detail_search_input.mako"/>

<%block name="main">
		<!-- InstanceBeginEditable name="main" -->
		<form action="${request.route_path("page_search_result")}" method="GET">
		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">フリーワードで探す</div></dt>
			<dd>
			  ${forms.query}
			</dd>
		  </dl>
		</div>

		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">ジャンルで探す</div></dt>
			<dd>
			  <table>
				  <tbody>
					${forms.genre}
				  </tbody>
				</table>
			</dd>
		  </dl>
		</div>

		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">開催地で探す</div></dt>
			<dd>
			  <table>
				  <tbody>
					${forms.area}
				  </tbody>
			  </table>
			</dd>
		  </dl>
		</div>

		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">公演日で探す</div></dt>
			<dd>
			  ${ forms.performance_term }
			</dd>
		  </dl>
		</div>
		
		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">販売条件</div></dt>
			<dd>
			  ${ forms.deal_cond }
			</dd>
		  </dl>
		</div>

		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">付加サービス</div></dt>
			<dd>
			  ${ forms.added_service }
			</dd>
		  </dl>
		</div>

		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">発売日</div></dt>
			<dd>
			  ${ forms.about_deal }
			</dd>
		  </dl>
		</div>

		<div id="searchFormButton">
		  <ul>
			<li>
			  <a href="${request.route_path("page_search_input")}"><img src="/static/ticketstar/img/search/btn_clear.gif" alt="条件をクリア" name="clear_button"/></a>
			</li>
			<li><input type="image" src="/static/ticketstar/img/search/btn_search.gif" alt="検索" name="search_button"/></li>
		  </ul>
		</div>
	</form>
</%block>

<%block name="side">
		<div class="sideCategoryGenre">
		<h2>特集</h2>
		<ul>
			<li><a href="#">特集/ライブハウスへ行こう!!</a></li>
			<li><a href="#">ロックフェス特集</a></li>
			<li><a href="#">アニメぴあ</a></li>
		</ul>
		</div>
		<div class="sideCategoryGenre">
		<h2>ジャンル一覧</h2>
		<ul>
			<li><a href="#">J-POP・ROCK</a></li>
			<li><a href="#">海外ROCK・POPS</a></li>
			<li><a href="#">フェスティバル</a></li>
			<li><a href="#">ジャズ・フュージョン</a></li>
			<li><a href="#">アニメ音楽</a></li>
			<li><a href="#">演歌・邦楽</a></li>
			<li><a href="#">童謡・日本のうた</a></li>
			<li><a href="#">民族音楽</a></li>
			<li><a href="#">シャンソン</a></li>
			<li><a href="#">音楽その他</a></li>
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
			<dt><img src="../img/common/side_info_title.gif" alt="お知らせ" width="190" height="18" /></dt>
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


