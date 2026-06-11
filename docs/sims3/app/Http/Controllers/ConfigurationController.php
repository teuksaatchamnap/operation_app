<?php

namespace App\Http\Controllers;

use App\Models\Configuration;
use Illuminate\Http\Request;

class ConfigurationController extends Controller
{
    public function index(Request $request)
    {
        $query = Configuration::query();
        if($request->has('app')) {
            $query->where("app", $request->app);
        }
        return $query->get();
    }

    public function show($id)
    {
        return Configuration::find($id);
    }

    public function store(Request $request)
    {
        $mission = $request->all();
        return Configuration::create($mission);
    }

    public function update(Request $request)
    {
        $c = Configuration::findOrFail($request->id);
        $c->fill($request->all());
        $c->save();
        return $c;
    }

    public function destroy(Configuration $c)
    {
        return $c->delete();
    }
}
