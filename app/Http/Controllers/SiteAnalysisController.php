<?php

namespace App\Http\Controllers;

use App\Models\FactMonthly;
use App\Models\Kpi;
use App\Models\Objective;
use App\Models\Sims3\Platform as Sims3Platform;
use App\Models\Sims3\Site as Sims3Site;
use App\Models\Site;
use Carbon\Carbon;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class SiteAnalysisController extends Controller
{
    public function show(Site $site, Request $request): JsonResponse
    {
        $sims3Site = Sims3Site::where('Id_Site', $site->name)->first();

        if (! $sims3Site) {
            return response()->json(['error' => 'Site not found in Sims3 database'], 404);
        }

        $romName = $sims3Site->Platform
            ? Sims3Platform::where('Code_Platform', $sims3Site->Platform)->value('Mail_ROM')
            : null;

        $monthStr = $request->query('month', now()->format('Y-m'));
        $month = Carbon::parse($monthStr.'-01');

        $fact = FactMonthly::where('site_id', $site->id)
            ->where('month', $month)
            ->first();

        $kpis = Kpi::with('objectives')->get()->keyBy('col_name');

        $kpiDefinitions = [
            ['key' => 'bottles_per_day_ytd', 'label' => 'bottles/day exc WinS (YTD)', 'col_name' => 'bottles_per_day', 'periodicity' => 'ytd'],
            ['key' => 'bottles_per_day', 'label' => 'bottles/day exc WinS', 'col_name' => 'bottles_per_day', 'periodicity' => 'monthly'],
            ['key' => 'bottles_per_day_incl', 'label' => 'bottles/day', 'col_name' => null, 'periodicity' => null],
            ['key' => 'sales_volume', 'label' => 'Total sales (bot/month)', 'col_name' => 'sales_volume', 'periodicity' => 'monthly'],
            ['key' => 'tier', 'label' => 'Tier', 'col_name' => 'tier', 'periodicity' => 'monthly'],
            ['key' => 'days_open', 'label' => 'Days open', 'col_name' => 'days_open', 'periodicity' => 'monthly'],
            ['key' => 'water_loss', 'label' => 'Over waste (%)', 'col_name' => 'water_loss', 'periodicity' => 'monthly'],
            ['key' => 'has_3_workers', 'label' => 'Nb of Operator', 'col_name' => null, 'periodicity' => null],
            ['key' => 'consumers', 'label' => 'Beneficiaries', 'col_name' => 'consumers', 'periodicity' => 'monthly'],
            ['key' => 'penetration', 'label' => 'Penetration (%)', 'col_name' => null, 'periodicity' => null],
            ['key' => 'water_quality', 'label' => 'Water Quality', 'col_name' => 'who_compliance', 'periodicity' => 'monthly'],
        ];

        $kpiData = [];
        foreach ($kpiDefinitions as $def) {
            $value = null;
            $objective = null;

            if ($def['col_name'] && $fact) {
                if ($def['periodicity'] === 'ytd') {
                    $ytdRecords = FactMonthly::where('site_id', $site->id)
                        ->whereYear('month', $month->year)
                        ->where('month', '<=', $month)
                        ->whereNotNull($def['col_name'])
                        ->pluck($def['col_name']);

                    if ($ytdRecords->isNotEmpty()) {
                        $value = round($ytdRecords->avg());
                    }
                } else {
                    $value = $fact->{$def['col_name']};
                }

                $kpi = $kpis->get($def['col_name']);
                if ($kpi) {
                    $matchingObjective = Objective::where('kpi_id', $kpi->id)
                        ->where('start_date', '<=', $month)
                        ->where(fn ($q) => $q->whereNull('end_date')->orWhere('end_date', '>=', $month))
                        ->first();
                    $objective = $matchingObjective ? (float) $matchingObjective->value : null;
                }
            }

            if ($def['col_name'] === 'who_compliance' && $value !== null) {
                $value = $value ? 'Safe' : 'Unsafe';
            } elseif (is_numeric($value)) {
                $value = round((float) $value);
            }

            $kpiData[$def['key']] = [
                'label' => $def['label'],
                'value' => $value ?? 0,
                'objective' => $objective ?? 0,
            ];
        }

        return response()->json([
            'platform' => $sims3Site->Platform,
            'entrepreneur_name' => $sims3Site->Entrepreneur_English_Name,
            'start_working_date' => $sims3Site->Date_start_working,
            'advisor_name' => $sims3Site->Advisor_email,
            'rom_name' => $romName,
            'commune_name' => $sims3Site->Commune,
            'population_commune' => $sims3Site->Population,
            'households' => $sims3Site->Households,
            'kpis' => $kpiData,
        ]);
    }
}
