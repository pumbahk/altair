## summary widget output template
## 
<div class="summary">
  <dl>
	% for item in items:
	  <dt ${item["attr"]|n}>${item["label"]}</td>
      <dd>${h.base.nl_to_br(item["content"])|n}</dd>
    % endfor
  </dl>
</div>
