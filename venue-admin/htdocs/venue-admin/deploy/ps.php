<?php
header("Refresh: 10");
?>
<pre><?php
system("ps auxw | grep `whoami` | egrep -v '(apache2|ps|grep|awk|-bash|emacs|ssh)' | awk '{ print $2, $9, $10, $11 }'");
