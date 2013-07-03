<html>
  <body>
    ${engines}
    <table border=1>
      <tr>
	<th>route</th><th>min</th><th>max</th><th>statements</th>
      </tr>
      %for route, summary in reversed(sorted(summarizer.queries.items(), key=lambda q: q[1]['max'])):
      <tr>
	<td>${route}</td>
	<td>${summary['min']}</td>
	<td>${summary['max']}</td>
	<td nowrap="nowrap">
	  %for engine, statements in summary['statements'].items():
	  ${engine}:${engines.get(engine)}
	  <ul>
	    %for stmt in statements:
	    <li>${stmt}</li>
	    %endfor
	  </ul>
	  %endfor
	</td>
      </tr>
      %endfor
  </body>
</html>
