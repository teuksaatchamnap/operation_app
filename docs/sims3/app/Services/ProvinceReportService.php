<?php

namespace App\Services;

use App\Helpers\KhmerLunarDate;
use App\Services\TierService;
use Carbon\Carbon;
use Illuminate\Support\Facades\DB;

class ProvinceReportService
{
    private const PROVINCE_NAMES_KH = [
        'Kandal'           => 'កណ្តាល',
        'Kratie'           => 'ក្រចេះ',
        'Kampong Cham'     => 'កំពង់ចាម',
        'Kampong Chhnang'  => 'កំពង់ឆ្នាំង',
        'Kampong Thom'     => 'កំពង់ធំ',
        'Kampong Speu'     => 'កំពង់ស្ពឺ',
        'Kampot'           => 'កំពត',
        'Takeo'            => 'តាកែវ',
        'Tbong Khmum'      => 'ត្បូងឃ្មុំ',
        'Banteay Meanchey' => 'បន្ទាយមានជ័យ',
        'Pailin'           => 'ប៉ៃលិន',
        'Battambang'       => 'បាត់ដំបង',
        'Pursat'           => 'ពោធិ៍សាត់',
        'Prey Veng'        => 'ព្រៃវែង',
        'Preah Vihear'     => 'ព្រះវិហារ',
        'Siem Reap'        => 'សៀមរាប',
        'Svay Rieng'       => 'ស្វាយរៀង',
        'Oddar Meanchey'   => 'ឧត្តរមានជ័យ',
    ];

    private const MONTH_NAMES_KH = [
        1 => 'មករា', 2 => 'កុម្ភះ', 3 => 'មិនា', 4 => 'មេសា',
        5 => 'ឧសភា', 6 => 'មិថុនា', 7 => 'កក្កដា', 8 => 'សីហា',
        9 => 'កញ្ញា', 10 => 'តុលា', 11 => 'វិច្ឆកា', 12 => 'ធ្នូ',
    ];

    /**
     * Provinces that have at least one site with sales in the given month.
     * Mirrors the SELECT DISTINCT Province ... query from the Python script.
     */
    public function listProvinces(Carbon $month): array
    {
        $monthStr = $month->copy()->startOfMonth()->toDateString();

        $rows = DB::table('Sites')
            ->join('Sales', 'Sites.Id_Site', '=', 'Sales.Id_Site')
            ->where('Sales.Month', $monthStr)
            ->where('Sales.Total_Sales', '>', 0)
            ->where('Sites.Platform', '<>', 'Dead')
            ->whereNotIn('Sites.Province', ['Dead', '', 'Stop'])
            ->distinct()
            ->orderBy('Sites.Province')
            ->pluck('Sites.Province')
            ->toArray();

        return array_map(function ($p) {
            $key = trim($p);
            return [
                'name'       => $p,
                'name_khmer' => self::PROVINCE_NAMES_KH[$key] ?? $p,
            ];
        }, $rows);
    }

    /**
     * Full data set for one province / one month, ready to feed the Blade template.
     */
    public function getProvinceData(Carbon $month, string $province): array
    {
        $monthStr = $month->copy()->startOfMonth()->toDateString();
        $lastYearDec = $month->copy()->subYear()->month(12)->day(1)->toDateString();
        $minus12 = $month->copy()->subMonths(12)->startOfMonth()->toDateString();
        $provinceKey = trim($province);
        $exchangeRate = TierService::exchangeRate($month);

        // Org-wide totals as of last year December (used in section 1 paragraph).
        $infoEndYear = DB::table('Sales')
            ->join('Sites', 'Sales.Id_Site', '=', 'Sites.Id_Site')
            ->where('Sales.Month', $lastYearDec)
            ->where('Sales.Total_Sales', '>', 0)
            ->where('Sites.Platform', '<>', 'Dead')
            ->selectRaw('COUNT(DISTINCT Sales.Id_Site) as total_sites, COUNT(DISTINCT CONCAT(Code_District, District)) as total_districts')
            ->first();

        $totalSitesPrevYear = (int) ($infoEndYear->total_sites ?? 0);
        $totalDistrictsPrevYear = (int) ($infoEndYear->total_districts ?? 0);

        // Aggregates for the province for the current month.
        // l_per_day: SUM/SUM ratio × 20 — matches ActivityIndicatorExport convention.
        // nb_active_sites: Total_Sales > 0 (NULL excluded by the comparison) — matches MD's "Sites with Sales".
        $salesTotal = DB::table('Sales')
            ->join('Sites', 'Sales.Id_Site', '=', 'Sites.Id_Site')
            ->where('Sales.Month', $monthStr)
            ->where('Sites.Province', $province)
            ->where('Sites.Platform', '<>', 'Dead')
            ->selectRaw('
                SUM(IFNULL(Total_Sales, 0) - IFNULL(Bottle_Sales, 0)) as sales_net,
                SUM(CASE WHEN Total_Sales > 0 THEN 1 ELSE 0 END) as nb_active_sites,
                SUM(IFNULL(WiS_Sales, 0)) as wins_sales,
                SUM(IFNULL(WiS_Income, 0)) as wins_income,
                CASE
                    WHEN SUM(Number_Open_Days) > 0
                    THEN SUM(IFNULL(Total_Sales, 0) - IFNULL(Bottle_Sales, 0)) / SUM(Number_Open_Days) * 20
                    ELSE 0
                END as l_per_day
            ')
            ->first();

        $beneficiariesTotal = (int) DB::table('Beneficiaries')
            ->join('Sites', 'Beneficiaries.Id_Site', '=', 'Sites.Id_Site')
            ->where('Beneficiaries.Month', $monthStr)
            ->where('Sites.Province', $province)
            ->where('Sites.Platform', '<>', 'Dead')
            ->sum('Beneficiaries.Beneficiaries');

        // Sales per site this month (used to detect Active/Inactive — Total_Sales > 0).
        $salesPerSite = DB::table('Sites')
            ->join('Sales', 'Sites.Id_Site', '=', 'Sales.Id_Site')
            ->where('Sales.Month', $monthStr)
            ->where('Sales.Total_Sales', '>', 0)
            ->where('Sites.Province', $province)
            ->where('Sites.Platform', '<>', 'Dead')
            ->select('Sites.Id_Site', DB::raw('(Total_Sales - Bottle_Sales) as net_sales'))
            ->get()
            ->keyBy('Id_Site');

        // All sites in the province with sales in the last 12 months.
        $sites = DB::table('Sites')
            ->join('Sales', 'Sites.Id_Site', '=', 'Sales.Id_Site')
            ->where('Sales.Month', '<=', $monthStr)
            ->where('Sales.Month', '>', $minus12)
            ->where('Sites.Province', $province)
            ->where('Sites.Platform', '<>', 'Dead')
            ->select(
                'Sites.Id_Site',
                'Sites.Commune',
                'Sites.District',
                'Sites.Commune_khmer',
                'Sites.District_khmer',
                'Sites.Land_of_kiosk',
                'Sites.Number_Population',
                'Sites.NumberSchoolsWinS',
                'Sites.NumberStudentsWinS',
                DB::raw('SUM(Total_Sales - Bottle_Sales) as net_sales')
            )
            ->groupBy(
                'Sites.Id_Site',
                'Sites.Commune',
                'Sites.District',
                'Sites.Commune_khmer',
                'Sites.District_khmer',
                'Sites.Land_of_kiosk',
                'Sites.Number_Population',
                'Sites.NumberSchoolsWinS',
                'Sites.NumberStudentsWinS'
            )
            ->orderBy('Sites.Id_Site')
            ->get();

        // First month with sales per site (= starting date).
        $startingDates = DB::table('Sales')
            ->join('Sites', 'Sales.Id_Site', '=', 'Sites.Id_Site')
            ->where('Sites.Province', $province)
            ->where('Sites.Platform', '<>', 'Dead')
            ->groupBy('Sales.Id_Site')
            ->select('Sales.Id_Site', DB::raw('MIN(Month) as starting_month'))
            ->get()
            ->keyBy('Id_Site');

        // Operators count for the month.
        $operators = DB::table('Indicators')
            ->where('Month', $monthStr)
            ->select('Id_Site', 'Number_of_Operator')
            ->get()
            ->keyBy('Id_Site');

        // Beneficiaries per site for the month.
        $beneficiariesPerSite = DB::table('Beneficiaries')
            ->where('Month', $monthStr)
            ->select('Id_Site', DB::raw('IFNULL(Beneficiaries, 0) as beneficiaries'))
            ->get()
            ->keyBy('Id_Site');

        $rows = [];
        $idx = 1;
        foreach ($sites as $site) {
            $idSite = $site->Id_Site;
            $hasSales = isset($salesPerSite[$idSite]);
            $startingMonth = $startingDates[$idSite]->starting_month ?? null;

            $beneficiariesCount = $hasSales
                ? (int) ($beneficiariesPerSite[$idSite]->beneficiaries ?? 0)
                : null;

            $pop = (int) ($site->Number_Population ?? 0);
            $pct = ($hasSales && $pop > 0 && $beneficiariesCount !== null)
                ? round(($beneficiariesCount / $pop) * 100, 1)
                : null;

            $rows[] = [
                'index'             => $idx++,
                'id_site'           => $idSite,
                'commune'           => $site->Commune_khmer ?: $site->Commune,
                'district'          => $site->District_khmer ?: $site->District,
                'starting_date'     => $startingMonth ? Carbon::parse($startingMonth)->format('m-Y') : '',
                'land_of_kiosk'     => $this->convertNumbers($site->Land_of_kiosk ?? ''),
                'beneficiaries'     => $beneficiariesCount,
                'beneficiaries_pct' => $pct,
                'operators'         => $hasSales ? (int) ($operators[$idSite]->Number_of_Operator ?? 0) : null,
                'nb_schools'        => $hasSales ? (int) ($site->NumberSchoolsWinS ?? 0) : null,
                'nb_students'       => ($hasSales && (int) $site->NumberStudentsWinS !== 0)
                    ? (int) $site->NumberStudentsWinS
                    : null,
                'status'            => $hasSales ? 'សកម្ម' : 'អសកម្ម',
            ];
        }

        $nbSites = count($sites);
        $nbActiveSites = (int) ($salesTotal->nb_active_sites ?? 0);
        $nbInactiveSites = $nbSites - $nbActiveSites;
        $salesNet = (int) round($salesTotal->sales_net ?? 0);
        $winsSales = (int) round($salesTotal->wins_sales ?? 0);
        $winsPriceUsd = (int) round(($salesTotal->wins_income ?? 0) / max($exchangeRate, 1));
        $lPerDay = (int) round($salesTotal->l_per_day ?? 0);

        $year = $month->year;
        $monthNum = $month->month;
        $provinceKhmer = self::PROVINCE_NAMES_KH[$provinceKey] ?? $province;

        $defaultParagraphs = $this->buildDefaultParagraphs(
            $provinceKhmer,
            self::MONTH_NAMES_KH[$monthNum],
            convertEnglishToKhmer((string) $year),
            convertEnglishToKhmer((string) ($year - 1)),
            convertEnglishToKhmer((string) $totalSitesPrevYear),
            convertEnglishToKhmer((string) $totalDistrictsPrevYear),
            convertEnglishToKhmer((string) $nbSites),
            convertEnglishToKhmer((string) $nbInactiveSites),
            convertEnglishToKhmer((string) $nbActiveSites),
            convertEnglishToKhmer(number_format($beneficiariesTotal, 0, '.', ' ')),
            convertEnglishToKhmer(number_format($lPerDay, 0, '.', ' ')),
            convertEnglishToKhmer(number_format($salesNet, 0, '.', ' ')),
            convertEnglishToKhmer(number_format($winsSales, 0, '.', ' ')),
            convertEnglishToKhmer(number_format($winsPriceUsd, 0, '.', ' '))
        );

        return [
            'province' => [
                'name'       => $province,
                'name_khmer' => $provinceKhmer,
            ],
            'month'         => [
                'year'      => $year,
                'month'     => $monthNum,
                'year_kh'   => convertEnglishToKhmer((string) $year),
                'month_kh'  => self::MONTH_NAMES_KH[$monthNum],
                'label_kh'  => self::MONTH_NAMES_KH[$monthNum] . ' ' . convertEnglishToKhmer((string) $year),
            ],
            'exchange_rate' => $exchangeRate, // sourced from TierService::exchangeRate($month)
            'totals' => [
                'nb_sites'             => $nbSites,
                'nb_active_sites'      => $nbActiveSites,
                'nb_inactive_sites'    => $nbInactiveSites,
                'beneficiaries'        => $beneficiariesTotal,
                'sales_net'            => $salesNet,
                'wins_sales'           => $winsSales,
                'wins_price_usd'       => $winsPriceUsd,
                'l_per_day'            => $lPerDay,
            ],
            'paragraphs' => $defaultParagraphs,
            'header'     => $this->buildDefaultHeader($month),
            'footer'     => $this->buildDefaultFooter(),
            'table'      => [
                'title'  => 'ស្ថានីយផលិតទឹកសហគមន៍ខេត្ត' . $provinceKhmer,
                'period' => 'លទ្ធផល ប្រចាំខែ ' . self::MONTH_NAMES_KH[$monthNum] . ' ឆ្នាំ' . convertEnglishToKhmer((string) $year),
                'rows'   => $rows,
            ],
        ];
    }

    private function convertNumbers(string $text): string
    {
        return convertEnglishToKhmer($text);
    }

    private function buildDefaultHeader(Carbon $month): array
    {
        $endOfMonth = $month->copy()->endOfMonth();
        $lunar      = (new KhmerLunarDate())->format($endOfMonth);
        $gregorian  = sprintf(
            'ភ្នំពេញ ថ្ងៃទី%s ខែ%s ឆ្នាំ%s',
            convertEnglishToKhmer((string) $endOfMonth->day),
            self::MONTH_NAMES_KH[$endOfMonth->month],
            convertEnglishToKhmer((string) $endOfMonth->year)
        );

        return [
            'kingdom_line_1'  => 'ព្រះរាជាណាចក្រកម្ពុជា',
            'kingdom_line_2'  => 'ជាតិ សាសនា ព្រះមហាក្សត្រ',
            'org_line_1'      => 'អង្គការទឹកស្អាត ១០០១ ',
            'org_line_2'      => 'លេខ៖........................./ទស១០០១',
            'date_lunar'      => $lunar,
            'date_gregorian'  => $gregorian,
        ];
    }

    private function buildDefaultFooter(): array
    {
        return [
            'director_title' => 'នាយិកាប្រតិបត្តិ',
            'director_name'  => 'អាម៉ង់ឌីន ឆូស៊ីណង',
            'cc_title'       => 'ចម្លងជូន៖',
            'cc_lines'       => [
                '១. រដ្ឋបាលស្រុកគោលដៅទាំងអស់់',
                '២. រដ្ឋបាលឃុំ សង្កាត់គោលដៅទាំងអស់',
            ],
            'address'        => 'ការិយាល័យភ្នំពេញ៖ ផ្ទះលេខ១០០ ផ្លូវ ៩៥ សង្កាតបឹងត្របែក ខណ្ឌចំការមន រាជធានីភ្នំពេញ ព្រះរាជាណាចក្រកម្ពុជា។  ប្រអប់សំបុត្រលេខ ១៤៧២ ' . "\n" .
                'ទូរស័ព្ទលេខ៖ ០២៣ ២១៥ ៤២៧ អ៊ីម៉ែលៈ info@teuksaat1001.com, គេហទំព័រ www.teuksaat1001.com.។',
        ];
    }

    private function buildDefaultParagraphs(
        string $provinceKhmer,
        string $monthKh,
        string $yearKh,
        string $prevYearKh,
        string $totalSitesPrevYearKh,
        string $totalDistrictsPrevYearKh,
        string $nbSitesKh,
        string $nbInactiveSitesKh,
        string $nbActiveSitesKh,
        string $beneficiariesKh,
        string $lPerDayKh,
        string $salesNetKh,
        string $winsSalesKh,
        string $winsPriceUsdKh
    ): array {
        return [
            'salutation_1' => 'សូមគោរពជូន',
            'salutation_2' => 'ឯកឧត្តមអភិបាលនៃគណៈអភិបាលខេត្ត' . $provinceKhmer,
            'subject_label' => 'កម្មវត្ថុ៖ ',
            'subject_text'  => 'របាយការណ៍រីកចម្រើនស្តីពីការអនុវត្តគម្រោងផ្គត់ផ្គង់ទឹកពិសាអូវី នៅទីជនបទក្នុងខេត្ត' . $provinceKhmer,
            'reference_label' => 'យោង៖',
            'reference_text'  => "          - លិខិតលេខ ៣២៩៧ ស.ជ.ណ ចុះថ្ងៃទី២២ ខែវិច្ឆិកា ឆ្នាំ២០២៣ របស់ក្រសួងមហាផ្ទៃ ស្តីពីការទទួលស្គាល់លទ្ធផលអង្គសន្និបាតវិសាមញ្ញដោយអនុម័តសម្រេច ផ្លាស់ប្តូរលក្ខន្តិកៈ ផ្លាស់ប្តូរសមាសភាពថ្មីនៃរចនាសម្ព័ន្ធអង្គការទឹកស្អាត១០០១ ។\n          - កិច្ចព្រមព្រៀងសហប្រតិបត្តិការរវាងក្រសួងអភិវឌ្ឍន៍ជនបទ និងអង្គការទឹកស្អាត១០០១ ចុះថ្ងៃទី១ ខែមេសា ឆ្នាំ២០២៦។",
            'section1_title' => '១. សាវតាអង្គការ',
            'section1_text'  => "          អង្គការទឹកស្អាត១០០១ គឺជាអង្គការក្រៅរដ្ឋាភិបាលក្នុងស្រុកមួយដែលបានអនុវត្តសកម្មភាពផ្គត់ផ្គង់ទឹកសុវត្ថិភាពសម្រាប់បរិភោគដល់ប្រជាពលរដ្ឋនៅជនបទនៃប្រទេសកម្ពុជាចាប់តាំងពីឆ្នាំ២០០៥ បានចុះបញ្ជីជាផ្លូវការជាមួយក្រសួងមហាផ្ទៃក្នុងឆ្នាំ២០០៧ និងបានចុះកិច្ចព្រមព្រៀងសហប្រតិបត្តិការជាមួយក្រសួងអភិវឌ្ឍន៍ជនបទចាប់តាំងពីឆ្នាំ២០០៩។ បច្ចុប្បន្នអង្គការទឹកស្អាត១០០១ មានការិយាល័យតំណាងចំនួនប្រាំរួមមាន៖ ការិយាល័យកណ្តាលនៅរាជធានីភ្នំពេញ ការិយាល័យតំណាងនៅខេត្តបាត់ដំបង ការិយាល័យតំណាងខេត្តសៀមរាប ការិយាល័យតំណាងខេត្តកំពង់ចាម និងការិយាល័យតំណាងខេត្តកំពង់ស្ពឺ។ ចាប់តាំងពីការបង្កើតដំបូងរហូតមកដល់ឆ្នាំ{$prevYearKh} អង្គការទឹកស្អាត១០០១ បានសាងសង់ និងដាក់ឱ្យដំណើរការស្ថានីយផលិតទឹកពិសាចំនួន{$totalSitesPrevYearKh} ក្នុងស្រុកចំនួន{$totalDistrictsPrevYearKh} នៅក្នុងខេត្តគោលដៅចំនួន១៨ នៃប្រទេសកម្ពុជា។",
            'section2_title' => '២. សកម្មភាពសំខាន់ៗក្នុងការគាំទ្រដល់សហគ្រិន',
            'section2_text'  => "សកម្មភាពគាំទ្ររបស់អង្គការទឹកស្អាត១០០១ ដល់សហគ្រិនដើម្បីឱ្យស្ថានីយទឹកមាននិរន្តរភាព រួមមាន\n            ២.១. ការបណ្តុះបណ្តាលសហគ្រិន និងប្រតិបត្តិករ ការគ្រប់គ្រងហិរញ្ញវត្ថុ ការរៀបចំរបាយការណ៍វឌ្ឍនភាព\n            ២.២. ការផ្តល់ការប្រឹក្សាយោបល់ផ្នែកទីផ្សារ ការគ្រប់គ្រងប្រតិបត្តិការ\n            ២.៣. ការដោះស្រាយការងារបច្ចេកទេស ការធ្វើការគាំទ្រទីផ្សារតាមរយៈការប្រើស្លាកសញ្ញាអូវី។\n            ២.៤. ការផ្គត់ផ្គង់វត្ថុធាតុដើម និងឧបករណ៍សម្ភារៈ\n            ២.៥. ការប្រមូលសំណាកគុណភាពទឹក ការត្រួតពិនិត្យទៅលើបទដ្ឋានអនាម័យ",
            'section3_title' => '៣. លទ្ធផលសម្រេចបាន',
            'section3_text'  => [
                ["            គិតត្រឹមខែ{$monthKh}ឆ្នាំ{$yearKh}នេះ នៅក្នុងខេត្ត{$provinceKhmer} អង្គការទឹកស្អាត១០០១ បានសាងសង់ស្ថានីយផលិតទឹកសហគមន៍អូវីចំនួន ", false],
                [$nbSitesKh, true],
                [" ស្ថានីយ ក្នុងនោះមាន ", false],
                [$nbInactiveSitesKh, true],
                [" ស្ថានីយ អសកម្មមិនដំណើរការ មានស្ថានីយចំនួន ", false],
                [$nbActiveSitesKh, true],
                [" ស្ថានីយ កំពុងដំណើរការ ក្នុងការផលិត និងផ្គត់ផ្គង់ទឹកសុវត្ថិភាពជូនដល់ប្រជាពលរដ្ឋចំនួន ", false],
                [$beneficiariesKh, true],
                [" នាក់។ ចំនួនបរិមាណនៃការផលិតទឹកក្នុងមួយស្ថានីយជាមធ្យមប្រមាណ ", false],
                [$lPerDayKh, true],
                [" លីត្រ/ថ្ងៃ។\n\n            ស្ថានីយទឹកសហគមន៍អូវីទាំងអស់បានផលិតទឹកសរុបចំនួន ", false],
                [$salesNetKh, true],
                [" ប៊ីដុង សម្រាប់ផ្គត់ផ្គង់ជូនប្រជាពលរដ្ឋ លើសពីនេះ អង្គការទឹកស្អាត១០០១ ក៏បានឧបត្ថម្ភទឹក ចំនួន ", false],
                [$winsSalesKh, true],
                [" ប៊ីដុង ដែលស្មើនឹងទឹកប្រាក់ ", false],
                [$winsPriceUsdKh, true],
                [" ដុល្លារសហរដ្ឋអាមេរិក សម្រាប់ចែកជូនដោយឥតគិតថ្លៃដល់សិស្សសាលាបឋមសិក្សាក្នុងឃុំគោលដៅទាំងអស់នៅក្នុងខេត្ត។ ទិន្នន័យដូចបានបង្ហាញជូនភ្ជាប់ក្នុងតារាង លទ្ធផលសម្រេចបានរបស់អង្គការទឹកស្អាត១០០១។\n\n            អាស្រ័យដូចបានគោរពជម្រាបជូនខាងលើ សូម ", false],
                ["ឯកឧត្តមអភិបាលនៃគណៈអភិបាលខេត្ត", true],
                [" មេត្តាជ្រាបជាសេចក្តីរាយការណ៍ និងបន្តការគាំទ្រដល់បេសកកម្ម ក៏ដូចជាសកម្មភាពរបស់អង្គការទឹកស្អាត១០០១ ស្របទៅនឹងផែនការយុទ្ធសាស្រ្តជាតិស្តីពីការផ្គត់ផ្គង់ទឹកស្អាត និងលើកកម្ពស់អនាម័យជនបទឆ្នាំ២០១៤-២០២៥ របស់ក្រសួងអភិវឌ្ឍន៍ជនបទ និងស្របតាមគោលដៅអភិវឌ្ឍន៍ប្រកបដោយចីរភាពរបស់រាជរដ្ឋាភិបាលកម្ពុជា ឆ្នាំ២០១៦-២០៣០ ដោយសេចក្តីអនុគ្រោះ។\n\n            សូម ", false],
                ["ឯកឧត្តមអភិបាល", true],
                [" មេត្តាទទួលនូវការគោរពដ៏ស្មោះស្ម័គ្រអំពីនាងខ្ញុំ។", false],
            ],
        ];
    }
}
