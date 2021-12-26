<?php
error_reporting(E_ALL);
ini_set('display_errors',1);
// POST
if( count($_POST)==2  && isset($_POST['file']) && isset($_POST['content']) ) {
    $name=pathinfo($_POST['file'])['basename'];
    //error_log($_POST['content']);
    file_put_contents($name, $_POST['content'], LOCK_EX);
}
// GET
// elseif( count($_GET)==1 && isset($_GET['file']) ) {
//     echo $_GET['file'];
// }
else {
    http_response_code(500);
    exit;
}
