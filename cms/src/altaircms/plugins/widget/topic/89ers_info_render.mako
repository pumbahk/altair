<% import itertools %>
<table class="info">
	<tr>
		<td>
		  %for i, topic in itertools.izip(itertools.count(1),topics):
		    <h4><span class="order">${i}.</span>${topic.title|n}</h4>
			${topic.text|n}
		  %endfor
		</td>
	</tr>
</table>
