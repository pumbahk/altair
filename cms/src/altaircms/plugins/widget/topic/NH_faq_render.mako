<dl class="faq">
  %for topic in topics:
    <dt>${topic.title|n}</td>
	<dd>${topic.text|n}</dd>
  %endfor
</dl>
