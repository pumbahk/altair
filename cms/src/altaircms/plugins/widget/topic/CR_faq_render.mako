<dl class="faq">
  %for topic in topics:
    <dt>${topic.title|n}</dt>
	<dd>${topic.text|n}</dd>
  %endfor
</dl>
