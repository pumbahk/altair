<html>
  <body>
    <table>
      <tr>
	<th>route</th><th>min</th><th>max</th><th>statements</th>
      </tr>
      %for route, summary in reversed(sorted(summarizer.queries.items(), key=lambda q: q[1]['max'])):
      <tr>
	<td>${route}</td>
	<td>${summary['min']}</td>
	<td>${summary['max']}</td>
	<td nowrap="nowrap">
	  <ul>
	    %for stmt in summary['statements']:
	    <li>${stmt}</li>
	    %endfor
	  </ul>
	</td>
      </tr>
      %endfor
  </body>
</html>
