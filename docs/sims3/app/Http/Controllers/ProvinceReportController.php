<?php

namespace App\Http\Controllers;

use App\Exports\ProvinceReportExport;
use App\Services\ProvinceReportService;
use Carbon\Carbon;
use Illuminate\Http\Request;
use Throwable;

class ProvinceReportController extends Controller
{
    public function __construct(private ProvinceReportService $service) {}

    /**
     * GET /api/provinceReport/provinces?month=YYYY-MM-DD
     */
    public function provinces(Request $request)
    {
        $month = $request->query('month')
            ? Carbon::parse($request->query('month'))->startOfMonth()
            : Carbon::now()->subMonthNoOverflow()->startOfMonth();

        return response()->json([
            'month'     => $month->format('Y-m-d'),
            'provinces' => $this->service->listProvinces($month),
        ]);
    }

    /**
     * GET /api/provinceReport/download?month=YYYY-MM-DD&province=Battambang&format=docx
     */
    public function download(Request $request)
    {
        $validated = $request->validate([
            'month'    => 'required|date',
            'province' => 'required|string',
            'format'   => 'nullable|in:docx,odt',
        ]);

        $format = $validated['format'] ?? 'docx';
        $month  = Carbon::parse($validated['month'])->startOfMonth();

        try {
            $data   = $this->service->getProvinceData($month, $validated['province']);
            $writer = (new ProvinceReportExport())->createWriter($data, $format);
        } catch (Throwable $e) {
            return response()->json([
                'message' => 'Failed to build the report.',
                'error'   => $e->getMessage(),
            ], 500);
        }

        $mimeType = $format === 'odt'
            ? 'application/vnd.oasis.opendocument.text'
            : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';

        $filename = sprintf(
            'Province Report - %s - %04d-%02d.%s',
            $validated['province'],
            $month->year,
            $month->month,
            $format
        );

        return response()->stream(
            fn () => $writer->save('php://output'),
            200,
            [
                'Content-Type'        => $mimeType,
                'Content-Disposition' => 'attachment; filename="' . $filename . '"',
                'Cache-Control'       => 'no-store, no-cache, must-revalidate, max-age=0',
                'Pragma'              => 'no-cache',
            ]
        );
    }
}
