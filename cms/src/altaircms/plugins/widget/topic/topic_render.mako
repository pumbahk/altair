<div class="topic-widget">
  <ul id="topics">
	%for topic in topics:
	  <li><a href="${topic.text}">${topic.title}</li>
	%endfor
  </ul>
</div>
