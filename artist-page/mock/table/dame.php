<?php
$a = array(
    'a/b' => 0,
    'a/b/c/d/e' => 1,
    'a/b/c' => 2,
    'a/b/c/d' => 3,
    'a/b/c/d/e/f/g' => 4,
    'a' => 5
);

$a_keys = array_keys($a);
print_r($a_keys);

foreach ($a_keys as $k) {
    echo $k, "\n";
    $a[$k. '/f'] = -2;
}
print_r($a_keys);
print_r($a);
