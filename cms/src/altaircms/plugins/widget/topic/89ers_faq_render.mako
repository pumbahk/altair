<dl class="faq">
  %for topic in topics:
    <% link = h.link.get_link_from_topic(request, topic) %>
    %if link:
	  <dt>${topic.title}</td>
	  <dd><a href="${link}">${topic.text}</a></dd>
	%else:
	  <dt>${topic.title}</td>
	  <dd>${topic.text}</dd>
    %endif
  %endfor
</dl>
