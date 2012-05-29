<div class="sideCategoryGenre">
  <ul>
	%for topic in topics:
	  <li><a href="${h.link.get_link_from_topic(request,topic)}">${topic.title}</a></li>
	%endfor
  </ul>
</div>
