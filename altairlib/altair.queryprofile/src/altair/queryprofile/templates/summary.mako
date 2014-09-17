<html>
<head>
  <title>Altair Query Profile</title>
  <style type="text/css">
body {
  position: relative;
  padding-top: 50px
}

.badge {
  border-radius: 1em;
  border: none;
  background-color: #888;
  padding: 0px 6px;
  font-weight: bold;
  color: #fff;
}

.badge-color-0 { background-color: #90CA77; }
.badge-color-1 { background-color: #81C6DD; }
.badge-color-2 { background-color: #E9B64D; }
.badge-color-3 { background-color: #E48743; }
.badge-color-4 { background-color: #9E3B33; }

.small {
  font-size: 0.75em;
  line-height: 1em;
}

.scrollable {
  height: 10em;
  overflow: scroll;
}

.expandable-list-item .indicator {
  margin-left: 0.5em;
}

.expandable-list-item.expanded .expandable-list-item-content {
  display: block;
}

.expandable-list-item.collapsed .expandable-list-item-content {
  display: none;
}
</style>
  <script type="text/javascript">
$(function () {
$(document.body).delegate('*[@data-toggle="expandable-list-item"]', 'click', function() {
  var $li = $(this).closest('.expandable-list-item');
  var $ind = $li.find('.indicator');
  if ($li.hasClass('collapsed')) {
    $li.removeClass('collapsed');
    $li.addClass('expanded');
    $ind.removeClass('icon-chevron-down');
    $ind.addClass('icon-chevron-up');
  } else {
    $li.removeClass('expanded');
    $li.addClass('collapsed');
    $ind.removeClass('icon-chevron-up');
    $ind.addClass('icon-chevron-down');
  }
});
});
</script>
</head>
<body>
  <div class="navbar navbar-inverse navbar-fixed-top">
    <div class="navbar-inner">
      <div class="container">
        <a class="brand">Altair Query Profiler</a>
      </div>
    </div>
  </div>
  <div class="container">
    <h2>Engines</h2>
    <table class="table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Connection String</th>
        </tr>
      </thead>
      <tbody>
      % for i, engine in sorted(engines.values(), key=lambda p:p[0]):
        <tr>
          <td><span class="badge badge-color-${i}">${i}</span></td>
          <td>${engine}</td>
        </tr>
      % endfor
    </table>
    <h2>Queries</h2>
    <ul>
    % for route, summary in reversed(sorted(queries.items(), key=lambda q: q[1]['max'])):
      <li class="expandable-list-item collapsed">
        <div class="expandable-list-item-header"><a data-toggle="expandable-list-item">${route}</a> (min: <span class="summary-min">${summary['min']}</span>, max: <span class="summary-max">${summary['max']}</span>)<span class="indicator icon-chevron-down"></span></div>
        <div class="expandable-list-item-content">
          <table class="table">
            <thead>
              <tr>
                <th>Engine</th>
                <th>Duration</th>
                <th>Statement</th>
              </tr>
            </thead>
            <tbody>
              %for engine, statements in sorted(summary['statements'].items(), key=lambda p:engines.get(p[0])[0]):
              %for stmt in statements:
              <tr>
                <td><span class="badge badge-color-${engines.get(engine)[0]}">${engines.get(engine)[0]}</span></td>
                <td>${'{0:.4f}s'.format(stmt['duration'])}</td>
                <td>
                  <pre class="small scrollable">${stmt['statement']}</pre>
                </td>
              </tr>
              %endfor
              %endfor
            </tbody>
          </table>
        </div>
      </li>
    % endfor
    </ul>
  </div>
</body>
</html>
