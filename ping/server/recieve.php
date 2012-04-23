<?php
$_GET['device'] = preg_replace('/[^0-9a-z_]+/i', '', $_GET['device']);
file_put_contents('data/pings.'.sha1($_GET['key']).'.'.$_GET['device'].'.txt', time()."\n", FILE_APPEND);
