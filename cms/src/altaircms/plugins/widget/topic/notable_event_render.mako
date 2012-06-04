## sizeがwidth,height固定はひどい

<div id="notableEvents">
  % for t in topcontents:
  <div class="event">
	<dl>
	  <dt><a href="${h.link.get_link_from_topic(request, t)}">${t.title }</a></dt>
	  <dd>${t.text}</dd>
	</dl>
	<p>
	  <a href="${h.link.get_link_from_topic(request, t)}">
		<img src="${h.asset.to_show_page(request, t.image_asset)}" alt="${t.title  }" width="80" height="80" />
	  </a><br />
	  <a>${t.countdown_type_ja}まであと${h.base.countdown_days_from(t.countdown_limit)}日</a></p>
  </div>
  % endfor
</div>
