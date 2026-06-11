<?php

namespace App\Http\Controllers;

use App\Imports\Test1Import;
use App\Mail\DeleteConsumable;
use App\Mail\RequestConsumable;
use App\Mail\ValidateConsumable;
use App\Models\Consumable;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Mail;
use Maatwebsite\Excel\Facades\Excel;

class ConsumableController extends Controller
{
    /**
     * Display a listing of the resource.
     */

    public function index(Request $request)
    {
        $email = $request->email;
        $dateapproval = $request->dateapproval;

        $consumables = consumable::where('EmailRequestor', $email)
            ->where('Date_submission', $dateapproval)
            ->where(function ($query) {
                $query->where('Validate', 0)->orWhereNull('Validate');
            })
            ->get();

        return response()->json($consumables);
    }
    public function uploadExcel(Request $request)
    {

        $request->validate([
            'file' => 'required|mimes:xlsx,xls',
        ]);
        $e = auth()->user()->email;
        $data = User::select('manager')->where('email', $e)->first();
        //$email = auth()->check() ? auth()->user()->email : null;
        $file = $request->file('file');
        //$import = new Test1Import($email);
        $import = new Test1Import();
        Excel::import($import, $file);
        if ($import->failures()->isNotEmpty()) {
            //return back()->withErrors($import->failures());
            return response()->json([
                'message' => 'no file in site.',
                'errors' => $import->failures(),
            ], 422);
        }
        $items = [
            'totalQty' => $import->totalQty,
            'email' => $e,
            'today' => now()->format('Y-m-d'),
            'manager' => $data->manager,

        ];

       if ($import->failures()->isEmpty() && $import->countInserted > 0) {
            $this->sendMailValidateItem($items);
        }
        //$totalQty = $import->getTotalQty();
        // $insertedRecords = $import->countRecord();
        return response()->json([
            'message' => 'File uploaded successfully.',
            'totalQty' => $import->totalQty,
            'inserted_records' => $import->countInserted,
            'missing_site_count' => $import->missingSiteCount,
            'success' => true // Add this flag
        ], 200);
    }
    private function sendMailValidateItem($items)
    {
        $recipients = [];
        $amount = intval($items['totalQty'] / 4000);

        if ($amount > 300) {
            $recipients = ['amandine.chaussinand@teuksaat1001.com', $items['email'], $items['manager']];
            $recipients1 = ['chamnap.keo@teuksaat1001.com'];
        } else {
            $recipients = [$items['email'], $items['manager']];
             $recipients1 = ['info@teuksaat1001.com'];
        }
        //$recipients1 = ['chamnap.keo@teuksaat1001.com'];

        Mail::to($recipients)->send(new RequestConsumable($items));
    }
    private function validateRequest($site,$sender,$manager,$managerEmail)
    {
        $recipients1 = ['chamnap.keo@teuksaat1001.com'];
        $recipients = ['finance@teuksaat1001.com','dina.d@teuksaat1001.com','sorvy.m@teuksaat1001.com','sreyrath.h@teuksaat1001.com','porleng.h@teuksaat1001.com','chamroeun.no@teuksaat1001.com',$sender,$manager,$managerEmail];
        Mail::to($recipients)->send(new ValidateConsumable($site,$manager));
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
    public function show(consumable $consumable)
    {
        //
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(consumable $consumable)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, consumable $consumable)
    {
        $email = $request->email;
        $dateapproval = $request->dateapproval;
        $manager =auth()->user()->email;
        $emailManager = User::select('manager')->where('email', $email)->first();
        // Get only unvalidated consumables
        $consumables = consumable::where('EmailRequestor', $email)
            ->where('Date_submission', $dateapproval)
            ->where(function ($query) {
                $query->where('Validate', 0)->orWhereNull('Validate');
            })
            ->get();

        // Group them by 'Id_Site'
        $groupedBySite = $consumables->groupBy('Id_Site');
        $siteList = $groupedBySite->keys()->all(); // returns an array like ['A1', 'A2', 'A3']

        // Optional: Convert to comma-separated string
        $siteListString = implode(', ', $siteList);
      // dd($siteListString);
        // Update only those not yet validated
        $updated = consumable::where('EmailRequestor', $email)
            ->where('Date_submission', $dateapproval)
            ->where(function ($query) {
            $query->where('Validate', 0)->orWhereNull('Validate');
            })
            ->update([
            'Validate' => 1,
            'EmailApprover' => auth()->user()->email,
            ]);

        if ($updated > 0) {
            $this->validateRequest($siteListString,$email,$manager,$emailManager->manager);
            return response()->json([
                'message' => 'Consumables updated successfully.',
            ], 200);
        } else {
            return response()->json([
                'message' => 'All consumables are already validated.',
            ], 200); // Change to 200 since it's not an error
        }
    }


    private function sendEmailDelete($sender,$dateapproval,$message,$manager)
    {
        Mail::to($sender)->send(new DeleteConsumable($sender,$dateapproval,$message,$manager));
    }
    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Request $request, consumable $consumable)
    {
        $manager = auth()->user()->email;
        $email = $request->query('email');
        $dateapproval = $request->query('dateapproval');
        $reason = $request->query('reason');
       // dd($email,$dateapproval,$reason,$manager);
        $deleted = consumable::where('EmailRequestor', $email)
            ->where('Date_submission', $dateapproval)
            ->where('Validate', 0)
            ->delete();
        if ($deleted > 0) {
            $this->sendEmailDelete($email,$dateapproval,$reason,$manager);
            return response()->json([
                'message' => 'Consumables deleted successfully.',
            ], 200);

        } else {
            return response()->json([
                'message' => 'No consumables found to delete.',
            ], 404);
        }
    }
}
