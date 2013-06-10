<html>
  <body>
    <table>
      <tr>
	<th>route</th><th>min</th><th>max</th>
      </tr>
      %for route, summary in reversed(sorted(summarizer.queries.items(), key=lambda q: q[1]['max'])):
      <tr>
	<td>${route}</td>
	<td>${summary['min']}</td>
	<td>${summary['max']}</td>
      </tr>
      %endfor
  </body>
</html>
