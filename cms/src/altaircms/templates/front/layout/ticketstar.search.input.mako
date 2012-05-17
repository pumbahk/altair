<%inherit file="altaircms:templates/front/ticketstar/search/detail_search_input.mako"/>

<%block name="main">
		<!-- InstanceBeginEditable name="main" -->
		<form>
		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">フリーワードで探す</div></dt>
			<dd>
			  <input name="textfield" id="textfield" size="35" value="アーティスト名、公演名、会場名など" onblur="if(this.value=='') this.value='アーティスト名、公演名、会場名など';" onfocus="if(this.value=='アーティスト名、公演名、会場名など') this.value='';" type="text">

			  <input type="radio" name="search_cond" value="intersection">全てを含む
			  <input type="radio" name="search_cond" value="union">少なくとも1つを含む
			</dd>
		  </dl>
		</div>

		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">ジャンルで探す</div></dt>
			<dd>
			  <table>
				  <tbody>
					<tr>
					  <td class="mostleft"><input type="checkbox" name="genre" value="music">音楽</td>
					  <td>
						<input type="checkbox" name="sub_genre" value="jazz">ジャズ・フュージョン
						<input type="checkbox" name="sub_genre" value="jpop">J-POP・ROCK
						<input type="checkbox" name="sub_genre" value="enka">演歌・邦楽
						<input type="checkbox" name="sub_genre" value="enka">童謡・日本のうた
						<input type="checkbox" name="sub_genre" value="enka">アニメ音楽
						<input type="checkbox" name="sub_genre" value="enka">シャンソン
						<input type="checkbox" name="sub_genre" value="enka">海外ROCK・POPS
						<input type="checkbox" name="sub_genre" value="enka">民謡音楽
						<input type="checkbox" name="sub_genre" value="enka">フェスティバル
						<input type="checkbox" name="sub_genre" value="enka">音楽その他
					  </td>
					</tr>
					<tr>
					  <td class="mostleft"><input type="checkbox" name="genre" value="music">演劇</td>
					  <td>
						<input type="checkbox" name="sub_genre" value="jazz">ジャズ・フュージョン
						<input type="checkbox" name="sub_genre" value="jpop">J-POP・ROCK
						<input type="checkbox" name="sub_genre" value="enka">演歌・邦楽
						<input type="checkbox" name="sub_genre" value="enka">童謡・日本のうた
						<input type="checkbox" name="sub_genre" value="enka">アニメ音楽
						<input type="checkbox" name="sub_genre" value="enka">シャンソン
						<input type="checkbox" name="sub_genre" value="enka">海外ROCK・POPS
						<input type="checkbox" name="sub_genre" value="enka">民謡音楽
						<input type="checkbox" name="sub_genre" value="enka">フェスティバル
						<input type="checkbox" name="sub_genre" value="enka">音楽その他
					  </td>
					</tr>
					<tr>
					  <td class="mostleft"><input type="checkbox" name="genre" value="music">スポーツ</td>
					  <td>
						<input type="checkbox" name="sub_genre" value="jazz">ジャズ・フュージョン
						<input type="checkbox" name="sub_genre" value="jpop">J-POP・ROCK
						<input type="checkbox" name="sub_genre" value="enka">演歌・邦楽
						<input type="checkbox" name="sub_genre" value="enka">童謡・日本のうた
						<input type="checkbox" name="sub_genre" value="enka">アニメ音楽
						<input type="checkbox" name="sub_genre" value="enka">シャンソン
						<input type="checkbox" name="sub_genre" value="enka">海外ROCK・POPS
						<input type="checkbox" name="sub_genre" value="enka">民謡音楽
						<input type="checkbox" name="sub_genre" value="enka">フェスティバル
						<input type="checkbox" name="sub_genre" value="enka">音楽その他
					  </td>
					</tr>
					<tr>
					  <td class="mostleft"><input type="checkbox" name="genre" value="music">イベント・その他</td>
					  <td>
						<input type="checkbox" name="sub_genre" value="jazz">ジャズ・フュージョン
						<input type="checkbox" name="sub_genre" value="jpop">J-POP・ROCK
						<input type="checkbox" name="sub_genre" value="enka">演歌・邦楽
						<input type="checkbox" name="sub_genre" value="enka">童謡・日本のうた
						<input type="checkbox" name="sub_genre" value="enka">アニメ音楽
						<input type="checkbox" name="sub_genre" value="enka">シャンソン
						<input type="checkbox" name="sub_genre" value="enka">海外ROCK・POPS
						<input type="checkbox" name="sub_genre" value="enka">民謡音楽
						<input type="checkbox" name="sub_genre" value="enka">フェスティバル
						<input type="checkbox" name="sub_genre" value="enka">音楽その他
					  </td>
					</tr>
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
					<tr>
					  <td class="mostleft"><input type="checkbox" name="area" value="0">北海道</td>
					  <td>
						<input type="checkbox" name="prefecture">北海道
					  </td>
					</tr>
					<tr>
					  <td class="mostleft"><input type="checkbox" name="area">東北</td>
					  <td>
						<input type="checkbox" name="prefecture">青森県
						<input type="checkbox" name="prefecture">岩手県
						<input type="checkbox" name="prefecture">宮城県
						<input type="checkbox" name="prefecture">秋田県
						<input type="checkbox" name="prefecture">山形県
						<input type="checkbox" name="prefecture">福島県
					  </td>
					</tr>
					<tr>
					  <td class="mostleft"><input type="checkbox" name="area">関東・甲信越</td>
					  <td>
						<input type="checkbox" name="prefecture">青森県
						<input type="checkbox" name="prefecture">岩手県
						<input type="checkbox" name="prefecture">宮城県
						<input type="checkbox" name="prefecture">秋田県
						<input type="checkbox" name="prefecture">山形県
						<input type="checkbox" name="prefecture">福島県
					  </td>
					</tr>
					<tr>
					  <td class="mostleft"><input type="checkbox" name="area">中部・東海</td>
					  <td>
						<input type="checkbox" name="prefecture">青森県
						<input type="checkbox" name="prefecture">岩手県
						<input type="checkbox" name="prefecture">宮城県
						<input type="checkbox" name="prefecture">秋田県
						<input type="checkbox" name="prefecture">山形県
						<input type="checkbox" name="prefecture">福島県
					  </td>
					</tr>
					<tr>
					  <td class="mostleft"><input type="checkbox" name="area">近畿・北陸</td>
					  <td>
						<input type="checkbox" name="prefecture">青森県
						<input type="checkbox" name="prefecture">岩手県
						<input type="checkbox" name="prefecture">宮城県
						<input type="checkbox" name="prefecture">秋田県
						<input type="checkbox" name="prefecture">山形県
						<input type="checkbox" name="prefecture">福島県
					  </td>
					</tr>
					<tr>
					  <td class="mostleft"><input type="checkbox" name="area">中国・四国</td>
					  <td>
						<input type="checkbox" name="prefecture">青森県
						<input type="checkbox" name="prefecture">岩手県
						<input type="checkbox" name="prefecture">宮城県
						<input type="checkbox" name="prefecture">秋田県
						<input type="checkbox" name="prefecture">山形県
						<input type="checkbox" name="prefecture">福島県
					  </td>
					</tr>
					<tr>
					  <td class="mostleft"><input type="checkbox" name="area">九州沖縄</td>
					  <td>
						<input type="checkbox" name="prefecture">青森県
						<input type="checkbox" name="prefecture">岩手県
						<input type="checkbox" name="prefecture">宮城県
						<input type="checkbox" name="prefecture">秋田県
						<input type="checkbox" name="prefecture">山形県
						<input type="checkbox" name="prefecture">福島県
					  </td>
					</tr>
				  </tbody>
			  </table>
			</dd>
		  </dl>
		</div>

		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">公演日で探す</div></dt>
			<dd>
			  <select name="start_year" size="1">
				<option value="2012">2012</option>
				<option value="2012">2012</option>
				<option value="2012">2012</option>
				<option value="2012">2012</option>
				<option value="2012">2012</option>
				<option value="2012">2012</option>
  		　    </select>年
			  <select name="start_month" size="1">
				<option value="1">1</option>
				<option value="2">2</option>
				<option value="3">3</option>
				<option value="4">4</option>
				<option value="5">5</option>
				<option value="6">6</option>
				<option value="7">7</option>
				<option value="8">8</option>
				<option value="9">9</option>
				<option value="10">10</option>
				<option value="11">11</option>
				<option value="12">12</option>
  		　    </select>月

			  <select name="start_day" size="1">
				<option value="1">1</option>
				<option value="2">2</option>
				<option value="3">3</option>
				<option value="4">4</option>
				<option value="5">5</option>
				<option value="6">6</option>
				<option value="7">7</option>
				<option value="8">8</option>
				<option value="9">9</option>
				<option value="10">10</option>
				<option value="11">11</option>
				<option value="12">12</option>
  		　    </select>日

			  〜

			  <select name="end_year" size="1">
				<option value="2012">2012</option>
				<option value="2012">2012</option>
				<option value="2012">2012</option>
				<option value="2012">2012</option>
				<option value="2012">2012</option>
				<option value="2012">2012</option>
  		　    </select>年
			  <select name="end_month" size="1">
				<option value="1">1</option>
				<option value="2">2</option>
				<option value="3">3</option>
				<option value="4">4</option>
				<option value="5">5</option>
				<option value="6">6</option>
				<option value="7">7</option>
				<option value="8">8</option>
				<option value="9">9</option>
				<option value="10">10</option>
				<option value="11">11</option>
				<option value="12">12</option>
  		　    </select>月

			  <select name="end_day" size="1">
				<option value="1">1</option>
				<option value="2">2</option>
				<option value="3">3</option>
				<option value="4">4</option>
				<option value="5">5</option>
				<option value="6">6</option>
				<option value="7">7</option>
				<option value="8">8</option>
				<option value="9">9</option>
				<option value="10">10</option>
				<option value="11">11</option>
				<option value="12">12</option>
  		　    </select>日
			</dd>
		  </dl>
		</div>
		
		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">販売条件</div></dt>
			<dd>
			  <input type="radio" name="sales_cond" value="normal">一般
			  <input type="radio" name="sales_cond" value="early">先行
			</dd>
		  </dl>
		</div>

		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">付加サービス</div></dt>
			<dd>
			  <input type="checkbox" name="zaseki">座席選択可能
			  <input type="checkbox" name="adjust">お隣キープ
			  <input type="checkbox" name="2d">公式ニ次市場
			</dd>
		  </dl>
		</div>

		<div class="searchInput">
		  <dl>
			<dt><div class="searchInputHeader">発売日</div></dt>
			<dd>
			  <ul>
				<li>
				  <input type="checkbox" name="zaseki">
				  <select name="day" size="1">
					<option value="1">1</option>
					<option value="2">2</option>
					<option value="3">3</option>
					<option value="4">4</option>
					<option value="5">5</option>
					<option value="6">6</option>
					<option value="7">7</option>
					<option value="8">8</option>
					<option value="9">9</option>
					<option value="10">10</option>
					<option value="11">11</option>
					<option value="12">12</option>
				  </select>日以内に発送
				</li>
				<li>
				  <input type="checkbox">
				  発売終了まで<select name="day" size="1">
					<option value="1">1</option>
					<option value="2">2</option>
					<option value="3">3</option>
					<option value="4">4</option>
					<option value="5">5</option>
					<option value="6">6</option>
					<option value="7">7</option>
					<option value="8">8</option>
					<option value="9">9</option>
					<option value="10">10</option>
					<option value="11">11</option>
					<option value="12">12</option>
				  </select>日

				</li>
				<li>
				  <input type="checkbox"> 販売終了
				  <input type="checkbox"> 公演中止
				</li>
			</dd>
		  </dl>
		</div>

		<div id="searchFormButton">
		  <ul>
			<li><input type="image" src="/static/ticketstar/img/search/btn_clear.gif" alt="条件をクリア" name="clear_button"/></li>
			<li><input type="image" src="/static/ticketstar/img/search/btn_search.gif" alt="検索" name="cancel_button"/></li>
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


