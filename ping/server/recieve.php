<?php
$_GET['key'] = preg_replace('/[^0-9a-z_]+/i', '', $_GET['key']);
$_GET['device'] = preg_replace('/[^0-9a-z_]+/i', '', $_GET['device']);
file_put_contents('data/pings.'.$_GET['key'].'.'.$_GET['device'].'.txt', time()."\n", FILE_APPEND);
