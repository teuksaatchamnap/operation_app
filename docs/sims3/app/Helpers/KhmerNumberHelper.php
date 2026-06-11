<?php

function convertEnglishToKhmer($number) {
    $khmerNumbers = ['០', '១', '២', '៣', '៤', '៥', '៦', '៧', '៨', '៩'];
    $englishNumbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

    return str_replace($englishNumbers, $khmerNumbers, $number);
}