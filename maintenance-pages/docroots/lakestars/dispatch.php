<?php
if (preg_match('#^(?:DoCoMo|KDDI|SoftBank|Vodafone|J-Phone|Willcom)#', $_SERVER['HTTP_USER_AGENT'])) {
    include 'mobile.php';
} else {
    include 'nonmobile.php';
}
