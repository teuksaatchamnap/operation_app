<?php

namespace App\Http\Controllers;

use App\Models\Sensor;
use Illuminate\Http\Request;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\DB;

class SensorController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        // $sensor= Sensor::selectRaw('sensor_id,min(water) AS water_start,max(water) AS water_end,DATE(received_date) AS day')
        //      ->groupBy('received_date','sensor_id')->orderBy('received_date','DESC')->get();

        // $sensor = DB::table('sensors')
        //           ->select('sensor_id',DB::raw('DATE(received_date) AS day,MIN(water) As Start, MAX(water) AS End'))
        //           ->groupBy('day','sensor_id')
        //           ->orderBy('day','DESC')
        //           ->get();
        // $sensor = Sensor::limit(300)->orderBy('received_date','DESC')->get();
        $sensors = Sensor::with("site:Id_Site,sensor_id,Platform")
                    ->select([
                        'sensor_id',
                        DB::raw('DATE(received_date) as day'),
                        DB::raw('min(water) as water_start_of_day'),
                        DB::raw('max(water) as water_end_of_day'),
                        DB::raw('min(voltage) as voltage_start'),
                        DB::raw('max(voltage) as voltage_end'),
                        DB::raw('min(electricity) as electricity_start'),
                        DB::raw('max(electricity) as electricity_end'),
                        DB::raw('min(current) as current_start'),
                        DB::raw('max(current) as current_end'),
                        DB::raw('min(flowrate) as flowrate_start'),
                        DB::raw('max(flowrate) as flowrate_end'),
                    ])
                    ->whereHas("site")
                    ->where("water", ">", 0)
                    ->where("received_date", ">", "2024-02-01")
                    ->groupBy(["day", "sensor_id"])
                    ->orderByDesc('day')
                    ->limit(300)
                    ->get();
                    //->groupBy("site.Id_Site");
       
        return $sensors;
    }

    /**
     * Show the form for creating a new resource.
     */
    public function create()
    {
        //
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        //
    }

    /**
     * Display the specified resource.
     */
    public function show(Sensor $sensor)
    {
        //
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(Sensor $sensor)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, Sensor $sensor)
    {
        //
    }
    public function showTime()
    {
        $currentDateTime = Carbon::now();
        $newDateTime = Carbon::now()->addDays(5);
             
        if ($currentDateTime < $newDateTime)
        print_r($newDateTime->toDateTimeString());
    }
    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Sensor $sensor)
    {
        //
    }
}
