<%block name="sideFeature">
			<h2><img src="/static/ticketstar/img/index/title_feature.gif" alt="特集" width="246" height="36" /></h2>
		<div id="sideFeature">
			<ul>
				<li><a href="#">ポイント10倍キャンペーン実施中！『大相撲三月場所』マス席の他、希少な溜まり席も販売！</a></li>
				<li><a href="#">ポイント10倍キャンペーン実施中！『大相撲三月場所』マス席の他、希少な溜まり席も販売！</a></li>
				<li><a href="#">ポイント10倍キャンペーン実施中！『大相撲三月場所』マス席の他、希少な溜まり席も販売！</a></li>
			</ul>
		</div>
</%block>

<%block name="sideMyMenu">
		<div id="sideMyMenu">
			<h2><img src="/static/ticketstar/img/index/title_mymenu.gif" alt="マイメニュー" width="246" height="36" /></h2>
			<ul>
				<li><a href="#">お気に入り</a></li>
				<li><a href="#">予約購入したチケット</a></li>
				<li><a href="#">出品中のチケット</a></li>
				<li><a href="#">メルマガの購読</a></li>
			</ul>
		</div>
</%block>

<%block name="sideInfo">
		<dl id="sideInfo">
			<dt><img src="/static/ticketstar/img/index/title_info.gif" alt="お知らせ" width="244" height="26" /></dt>
			<dd>
				<ul>
					<li>2011年12月4日(日)　～　2011年12月4日(日)　メンテナンスを行います</li>
					<li>2011年12月4日(日)　～　2011年12月4日(日)　メンテナンスを行います</li>
				</ul>
			</dd>
		</dl>
</%block>

<%block name="sideBtn">
		<ul id="sideBtn">
			<li><a href="#"><img src="/static/ticketstar/img/index/btn_use.gif" alt="楽天チケットの使い方" width="242" height="28" /></a></li>
			<li><a href="#"><img src="/static/ticketstar/img/index/btn_campaign.gif" alt="新規入会特典2,000ポイントのところ今だけ入会特典増量中！" width="240" height="76" /></a></li>
		</ul>
</%block>

<%block name="facebook">
		<iframe src="//www.facebook.com/plugins/likebox.php?href=http%3A%2F%2Fwww.facebook.com%2Fpages%2F%25E3%2583%2596%25E3%2583%25AB%25E3%2583%25BC%25E3%2583%259E%25E3%2583%25B3%2F210488268963686&amp;width=240&amp;height=290&amp;colorscheme=light&amp;show_faces=true&amp;border_color&amp;stream=false&amp;header=true" scrolling="no" frameborder="0" style="border:none; overflow:hidden; width:240px; height:290px;" allowTransparency="true"></iframe>
</%block>

<%block name="twitter">
		<script charset="utf-8" src="http://widgets.twimg.com/j/2/widget.js"></script>
		<script>
		new TWTR.Widget({
		  version: 2,
		  type: 'profile',
		  rpp: 10,
		  interval: 30000,
		  width: 240,
		  height: 380,
		  theme: {
			shell: {
			  background: '#c01921',
			  color: '#ffffff'
			},
			tweets: {
			  background: '#ffffff',
			  color: '#000000',
			  links: '#5353f2'
			}
		  },
		  features: {
			scrollbar: true,
			loop: false,
			live: true,
			behavior: 'all'
		  }
		}).render().setUser('RakutenTicket').start();
		</script>
</%block>
