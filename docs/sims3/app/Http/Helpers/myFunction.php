<?php
    //  function Distance(
    //     $latitudeFrom, $longitudeFrom, $latitudeTo, $longitudeTo, $earthRadius = 6371000)
    //   {
    //     // convert from degrees to radians
    //     $latFrom = deg2rad($latitudeFrom);
    //     $lonFrom = deg2rad($longitudeFrom);
    //     $latTo = deg2rad($latitudeTo);
    //     $lonTo = deg2rad($longitudeTo);
      
    //     $latDelta = $latTo - $latFrom;
    //     $lonDelta = $lonTo - $lonFrom;
      
    //     $angle = 2 * asin(sqrt(pow(sin($latDelta / 2), 2) +
    //       cos($latFrom) * cos($latTo) * pow(sin($lonDelta / 2), 2)));
    //     return $angle * $earthRadius;
    //   }
    function Distance($lat1, $lon1, $lat2, $lon2, $unit) {
        if (($lat1 == $lat2) && ($lon1 == $lon2)) {
          return 0;
        }
        else {
          $theta = $lon1 - $lon2;
          $dist = sin(deg2rad($lat1)) * sin(deg2rad($lat2)) +  cos(deg2rad($lat1)) * cos(deg2rad($lat2)) * cos(deg2rad($theta));
          $dist = acos($dist);
          $dist = rad2deg($dist);
          $miles = $dist * 60 * 1.1515;
          $unit = strtoupper($unit);
      
          if ($unit == "K") {
            return ($miles * 1.609344);
          } else if ($unit == "N") {
            return ($miles * 0.8684);
          } else {
            return $miles;
          }
        }
      }
?>