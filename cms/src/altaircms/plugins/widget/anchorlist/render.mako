## anchorlist widget output template
## 
<div class="anchorlist-widget">
  <ul id="sideNav">
	% if headings:
		<li> <a href="#${headings[0].html_id}">${headings[0].text}</a></li>
	  % for heading in headings[1:]:
		<li> <a href="#${heading.html_id}">${heading.text}</a></li>
	  % endfor
	% endif
  </ul>
</div>
