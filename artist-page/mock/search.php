<?php
$doc = simplexml_load_file('http://api.rakuten.co.jp/rws/3.0/rest?developerId=12657057e6e263dfe5dd57b5565078da&operation=BooksCDSearch&version=2011-12-01&artistName=AI');
$doc->registerXPathNamespace('booksCDSearch', 'http://api.rakuten.co.jp/rws/rest/BooksCDSearch/2011-12-01');
foreach ($doc->xpath('Body/booksCDSearch:BooksCDSearch/Items/Item') as $item) {
    echo $item->title."\n";
}

?>