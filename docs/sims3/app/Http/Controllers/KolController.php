<?php

namespace App\Http\Controllers;

use App\Models\Kol;
use App\Models\SaleSurvey;
use Illuminate\Http\Request;
use Stichoza\GoogleTranslate\GoogleTranslate; 
class KolController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        return Kol::select('*')->get();
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $kol = $request->all();
        $kol = Kol::create($kol);
        return $kol;
    }

    /**
     * Display the specified resource.
     */
    public function show($id)
    {
        $kol = Kol::find($id);
        return $kol ;
    }
        /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, Kol $kol)
    {
         $kol->fill($request->all());
         $kol->save();
         return $kol;
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Kol $kol)
    {
        //
    }
     public function translate(Request $request)
    {
        // For testing, hardcoded text. Later, replace with $request->text
        $text = "sok_dara";
        $translated = $this->translateNameToKhmer($text);

        return response()->json([
            'original' => $text,
            'translated' => $translated,
        ]);
    }

    private function translateNameToKhmer(string $text): string
    {
        // 1. Custom dictionary for known Khmer names
        $dictionary = [
            'keo' => 'កែវ',
            'chamnap' => 'ចំណាប់',
            // Add more mappings as needed
        ];

        // 2. Split text by underscores or spaces
        $words = preg_split('/[_\s]+/', strtolower($text));

        // 3. Try to translate using dictionary
        $translatedWords = [];
        foreach ($words as $word) {
            if (isset($dictionary[$word])) {
                $translatedWords[] = $dictionary[$word];
            } else {
                // 4. Fallback: use Google Translate for unknown words
                try {
                    $translator = new GoogleTranslate('km');
                    $translatedWords[] = $translator->translate($word);
                } catch (\Exception $e) {
                    $translatedWords[] = $word; // fallback to original
                }
            }
        }

        // 5. Join translated words
        return implode(' ', $translatedWords);
    }

    public function translateName()
    {
        // Replace underscores with spaces for better translation interpretation
        $name= "keo_chamnap";
        $processedName = str_replace('_', ' ', $name);

        // Initialize the translator
        $tr = new GoogleTranslate();

        // Set the source language (English) and target language (Khmer)
        $tr->setSource('en')->setTarget('km');

        // Attempt to translate the name
        $khmerName = $tr->translate($processedName);

        // Return the result as a JSON response
        return response()->json([
            'original_english_name' => $name,
            'processed_for_translation' => $processedName,
            'translated_khmer_name' => $khmerName,
            'note' => 'Name translation (transliteration) can vary in accuracy. Always review for critical applications.'
        ]);
    }
    public function kolDownloadReport(Request $request)
    {
        $start_date = $request->query('start_date');
        $end_date = $request->query('end_date');

        // Validate date inputs
        if (!$start_date || !$end_date) {
            return response()->json(['error' => 'Start date and end date are required.'], 400);
        }
        $inputFileName = storage_path('app/templates/kol.xlsx');
        $reportData = Kol::whereBetween('record_date', [$start_date, $end_date])->get();
        $data = array();
        foreach($reportData as $sale)
        {
            $data[]= $sale->toArray();
        }
         // dd($data);
        $TBS = new \clsTinyButStrong;
        $ok = class_exists('clsOpenTBS', true);
        $TBS->OtbsMsExcelExplicitRef = false;
        $TBS->Plugin(\TBS_INSTALL, \OPENTBS_PLUGIN);
        $TBS->LoadTemplate($inputFileName, \OPENTBS_ALREADY_UTF8);
        $TBS->PlugIn(OPENTBS_SELECT_SHEET, 1);
        $TBS->SetOption("noerr", true);
        $TBS->MergeBlock('a', $data);
        $TBS->Show(OPENTBS_DOWNLOAD, "kol.xlsx");
    }
    public function saleSurvey()
    {
        return SaleSurvey::select('*')->limit(300)->get();
    }
}
