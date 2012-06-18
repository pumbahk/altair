## summary widget output template
## 
<div class="detailBox" id="settlementEventDetail">
  <div class="detailBoxInner">
	<h2><img src="/static/ticketstar/img/settlement/title_event.gif" alt="イベント詳細" width="106" height="29" /></h2>
	<table summary="イベント詳細情報">
	  % for item in items:
	  <tr>
	    <th scope="row">${item["label"]}</th>
		<td>${h.base.nl_to_br(item["content"])}</td>
      </tr>
      % endfor
	</table>
  </div>
</div>

## obsolete
<%doc>
<div class="summary">
  <dl>
	% for item in items:
	  ##<dt ${item["attr"]|n}>${item["label"]}</td>
      <dt>${item["label"]}</td>
      <dd>${h.base.nl_to_br(item["content"])}</dd>
    % endfor
  </dl>
</div>
</%doc>
