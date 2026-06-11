<?php

namespace App\Exports;

use PhpOffice\PhpWord\PhpWord;
use PhpOffice\PhpWord\IOFactory;
use PhpOffice\PhpWord\SimpleType\Jc;
use PhpOffice\PhpWord\Element\Section;
use PhpOffice\PhpWord\Writer\WriterInterface;

class ProvinceReportExport
{
    private const BLUE         = '00B0F0';
    private const FOOTER_BLUE  = '7FB6DE';
    private const BLACK        = '000000';
    private const WHITE        = 'FFFFFF';
    private const ORANGE_BG    = 'FCD5B4';

    // A4 = 11907 × 16839 twips. Margins match the reference document.
    private const PAGE_W        = 11907;
    private const MARGIN_TOP    = 810;
    private const MARGIN_BOTTOM = 1080;   // 19mm — leaves room above the page footer
    private const MARGIN_LEFT   = 720;
    private const MARGIN_RIGHT  = 720;
    private const FOOTER_DIST   = 360;    // 6.35mm from page-edge to footer

    // Content width (twips) = 11907 − 720 − 720 = 10467
    private const CONTENT_W = 10467;

    // Column widths (twips) for the 12-column results table — must sum to CONTENT_W
    private const COL_WIDTHS = [369, 782, 1166, 1166, 836, 1555, 972, 627, 729, 729, 731, 805];

    // ─────────────────────────────────────────────────────────────────────────

    public function createWriter(array $data, string $format = 'docx'): WriterInterface
    {
        $phpWord = new PhpWord();
        $phpWord->setDefaultFontName('Khmer OS Battambang');
        $phpWord->setDefaultFontSize(11);

        $this->buildLetterSection($phpWord, $data);
        $this->buildTableSection($phpWord, $data);

        return IOFactory::createWriter($phpWord, $format === 'odt' ? 'ODText' : 'Word2007');
    }

    // ─── Page settings ───────────────────────────────────────────────────────

    private function sectionSettings(bool $pageBreak = false): array
    {
        $s = [
            'paperSize'    => 'A4',
            'marginTop'    => self::MARGIN_TOP,
            'marginBottom' => self::MARGIN_BOTTOM,
            'marginLeft'   => self::MARGIN_LEFT,
            'marginRight'  => self::MARGIN_RIGHT,
            'footerHeight' => self::FOOTER_DIST,
        ];
        if ($pageBreak) {
            $s['breakType'] = 'nextPage';
        }
        return $s;
    }

    private function addPageFooter(Section $section, array $f): void
    {
        $footer = $section->addFooter();
        $address = trim((string) ($f['address'] ?? ''));
        if ($address === '') return;

        $lines = preg_split('/\r?\n/', $address);
        $font  = ['name' => 'Khmer OS Siemreap', 'size' => 7, 'color' => self::FOOTER_BLUE];

        foreach ($lines as $i => $line) {
            $line = trim($line);
            if ($line === '') continue;
            $para = [
                'alignment'  => Jc::CENTER,
                'spaceBefore' => 0,
                'spaceAfter'  => 0,
            ];
            if ($i === 0) {
                $para['borderTopSize']  = 6;
                $para['borderTopColor'] = self::FOOTER_BLUE;
            }
            $footer->addText($line, $font, $para);
        }

        $footer->addPreserveText(
            '{PAGE}',
            ['size' => 8, 'color' => self::FOOTER_BLUE, 'bold' => true],
            ['alignment' => Jc::END, 'spaceBefore' => 40, 'spaceAfter' => 0]
        );
    }

    // ─── Letter page ─────────────────────────────────────────────────────────

    private function buildLetterSection(PhpWord $phpWord, array $data): void
    {
        $section = $phpWord->addSection($this->sectionSettings());

        $h = $data['header']     ?? [];
        $p = $data['paragraphs'] ?? [];
        $f = $data['footer']     ?? [];

        $this->addPageFooter($section, $f);
        $this->addHeaderTable($section, $h);
        $this->addSalutation($section, $p);
        $this->addSubjectLine($section, $p);
        $this->addReferenceLine($section, $p);

        for ($i = 1; $i <= 3; $i++) {
            $this->addBodySection(
                $section,
                $p["section{$i}_title"] ?? '',
                $p["section{$i}_text"]  ?? ''
            );
        }

        $this->addSignature($section, $f);
        $this->addCcBlock($section, $f);
    }

    private function addHeaderTable(Section $section, array $h): void
    {
        $tableStyle = [
            'borderSize'       => 0,
            'borderColor'      => self::WHITE,
            'cellMarginTop'    => 0,
            'cellMarginBottom' => 0,
            'cellMarginLeft'   => 0,
            'cellMarginRight'  => 0,
        ];
        $table     = $section->addTable($tableStyle);
        $half      = (int) (self::CONTENT_W / 2);
        $noBorder  = $this->noBorderCell();
        $noSpacing = ['spaceBefore' => 0, 'spaceAfter' => 0];

        // ── Row 1: Kingdom lines — full width, centered ───────────────────────
        $table->addRow();
        $cellK = $table->addCell(self::CONTENT_W, array_merge($noBorder, ['gridSpan' => 2]));
        foreach (['kingdom_line_1', 'kingdom_line_2'] as $key) {
            if (!empty($h[$key])) {
                $cellK->addText(
                    $h[$key],
                    ['name' => 'Khmer OS Muol Light', 'size' => 11, 'color' => self::BLUE],
                    array_merge($noSpacing, ['alignment' => Jc::CENTER])
                );
            }
        }

        // ── Row 2: Logo + org name (left-aligned) | Date (right-aligned) ─────
        $table->addRow();

        $cellL    = $table->addCell($half, $noBorder);
        $logoPath = public_path('img/logo.png');
        if (file_exists($logoPath)) {
            $cellL->addImage($logoPath, ['width' => 70, 'wrappingStyle' => 'inline']);
        }
        foreach (['org_line_1', 'org_line_2'] as $key) {
            if (!empty($h[$key])) {
                $size = $key === 'org_line_1' ? 12 : 10;
                $cellL->addText(
                    $h[$key],
                    ['name' => 'Khmer OS Muol Light', 'size' => $size, 'color' => self::BLUE],
                    array_merge($noSpacing, ['alignment' => Jc::START])
                );
            }
        }

        $cellR  = $table->addCell($half, $noBorder);
        $italic = ['name' => 'Khmer OS Battambang', 'size' => 10, 'italic' => true];
        if (!empty($h['date_lunar'])) {
            $cellR->addText(
                $h['date_lunar'],
                $italic,
                ['alignment' => Jc::END, 'spaceBefore' => 1940, 'spaceAfter' => 0]
            );
        }
        if (!empty($h['date_gregorian'])) {
            $cellR->addText(
                $h['date_gregorian'],
                $italic,
                ['alignment' => Jc::END, 'spaceBefore' => 40, 'spaceAfter' => 0]
            );
        }
    }

    private function addSalutation(Section $section, array $p): void
    {
        $font  = ['name' => 'Khmer OS Muol Light', 'bold' => true, 'size' => 11];
        $para  = ['alignment' => Jc::CENTER, 'spaceBefore' => 240, 'spaceAfter' => 0];

        foreach (['salutation_1', 'salutation_2'] as $key) {
            if (!empty($p[$key])) {
                $section->addText($p[$key], $font, $para);
            }
        }
    }

    private function addSubjectLine(Section $section, array $p): void
    {
        $textRun = $section->addTextRun(['alignment' => Jc::START, 'spaceBefore' => 200, 'spaceAfter' => 0]);
        if (!empty($p['subject_label'])) {
            $textRun->addText($p['subject_label'], [
                'name'      => 'Khmer OS Muol Light',
                'bold'      => true,
                'underline' => 'single',
            ]);
        }
        if (!empty($p['subject_text'])) {
            $textRun->addText($p['subject_text']);
        }
    }

    private function addReferenceLine(Section $section, array $p): void
    {
        if (!empty($p['reference_label'])) {
            $section->addText(
                $p['reference_label'],
                ['name' => 'Khmer OS Muol Light', 'bold' => true, 'underline' => 'single'],
                ['spaceBefore' => 200, 'spaceAfter' => 0]
            );
        }
        $this->addMultilineText(
            $section,
            $p['reference_text'] ?? '',
            [],
            ['spaceBefore' => 0, 'spaceAfter' => 0, 'alignment' => Jc::BOTH]
        );
    }

    private function addBodySection(Section $section, string $title, string|array $text): void
    {
        if ($title !== '') {
            $section->addText(
                $title,
                ['name' => 'Khmer OS Muol Light', 'bold' => true, 'underline' => 'single'],
                ['spaceBefore' => 200, 'spaceAfter' => 0]
            );
        }

        if (is_array($text)) {
            $this->addRichText($section, $text);
        } else {
            $this->addMultilineText(
                $section,
                $text,
                [],
                ['spaceBefore' => 0, 'spaceAfter' => 0, 'alignment' => Jc::BOTH]
            );
        }
    }

    /**
     * Render [string, bool] run-pairs with proper paragraph structure.
     *
     * \n\n → new Word paragraph (so Jc::BOTH last-line rule resets)
     * \n   → <w:br/> soft line-break within the same paragraph
     *
     * This ensures single-line paragraphs (list items) are never stretched
     * by justification — Word's last-line exemption applies per paragraph.
     *
     * @param array<array{string, bool}> $runs
     */
    private function addRichText(Section $section, array $runs): void
    {
        $paraStyle = ['spaceBefore' => 0, 'spaceAfter' => 0, 'alignment' => Jc::BOTH];
        $baseFont  = ['name' => 'Khmer OS Battambang'];

        // Tokenise all runs into a flat stream:
        //   ['p']        → paragraph break (from \n\n)
        //   ['br']       → soft line-break (from \n)
        //   ['t', $text, $bold] → text run
        $tokens = [];
        foreach ($runs as [$runText, $bold]) {
            $paraChunks = explode("\n\n", $runText);
            foreach ($paraChunks as $pi => $paraChunk) {
                if ($pi > 0) {
                    $tokens[] = ['p'];
                }
                $lineChunks = explode("\n", $paraChunk);
                foreach ($lineChunks as $li => $lineChunk) {
                    if ($li > 0) {
                        $tokens[] = ['br'];
                    }
                    if ($lineChunk !== '') {
                        $tokens[] = ['t', $lineChunk, $bold];
                    }
                }
            }
        }

        $textRun = $section->addTextRun($paraStyle);
        foreach ($tokens as $token) {
            if ($token[0] === 'p') {
                $textRun = $section->addTextRun($paraStyle);
            } elseif ($token[0] === 'br') {
                $textRun->addTextBreak();
            } else {
                [, $text, $bold] = $token;
                $textRun->addText($text, $bold ? array_merge($baseFont, ['bold' => true]) : $baseFont);
            }
        }
    }

    private function addSignature(Section $section, array $f): void
    {
        $font  = ['name' => 'Khmer OS Muol Light', 'bold' => true];
        $right = ['alignment' => Jc::END, 'spaceBefore' => 0, 'spaceAfter' => 0];

        if (!empty($f['director_title'])) {
            $section->addText($f['director_title'], $font, ['alignment' => Jc::END, 'spaceBefore' => 360, 'spaceAfter' => 0]);
        }
        // Space for handwritten signature
        for ($i = 0; $i < 4; $i++) {
            $section->addText('', [], $right);
        }
        if (!empty($f['director_name'])) {
            $section->addText($f['director_name'], $font, $right);
        }
    }

    private function addCcBlock(Section $section, array $f): void
    {
        if (!empty($f['cc_title'])) {
            $section->addText(
                $f['cc_title'],
                ['name' => 'Khmer OS Muol Light', 'bold' => true],
                ['spaceBefore' => 200, 'spaceAfter' => 0]
            );
        }
        foreach ($f['cc_lines'] ?? [] as $line) {
            $section->addText($line, [], ['spaceBefore' => 0, 'spaceAfter' => 0]);
        }
    }

    // ─── Table page ───────────────────────────────────────────────────────────

    private function buildTableSection(PhpWord $phpWord, array $data): void
    {
        $section = $phpWord->addSection($this->sectionSettings(true));
        $table   = $data['table'] ?? [];

        $this->addPageFooter($section, $data['footer'] ?? []);
        $this->addTableTitles($section, $table['title'] ?? '', $table['period'] ?? '');
        $this->addResultsTable($section, $table['rows'] ?? []);
    }

    private function addTableTitles(Section $section, string $title, string $period): void
    {
        $boldMuol   = ['name' => 'Khmer OS Muol Light', 'bold' => true, 'size' => 10];
        $centerPara = ['alignment' => Jc::CENTER, 'spaceBefore' => 0, 'spaceAfter' => 0];

        $t = $section->addTable([
            'borderTopSize'     => 8, 'borderTopColor'     => self::BLACK,
            'borderLeftSize'    => 8, 'borderLeftColor'    => self::BLACK,
            'borderRightSize'   => 8, 'borderRightColor'   => self::BLACK,
            'borderBottomSize'  => 8, 'borderBottomColor'  => self::BLACK,
            'borderInsideHSize' => 8, 'borderInsideHColor' => self::BLACK,
            'borderInsideVSize' => 0, 'borderInsideVColor' => self::WHITE,
        ]);

        $t->addRow();
        $t->addCell(self::CONTENT_W)->addText($title, $boldMuol, $centerPara);
        $t->addRow();
        $t->addCell(self::CONTENT_W)->addText($period, $boldMuol, $centerPara);
    }

    private function addResultsTable(Section $section, array $rows): void
    {
        $cols       = self::COL_WIDTHS;
        $dataFont   = ['name' => 'Khmer OS Battambang', 'size' => 9];
        $headerFont = ['name' => 'Khmer OS Battambang', 'size' => 9, 'bold' => true];
        $centerPara = ['alignment' => Jc::CENTER, 'spaceBefore' => 0, 'spaceAfter' => 0];
        $rightPara  = ['alignment' => Jc::END,    'spaceBefore' => 0, 'spaceAfter' => 0];
        $leftPara   = ['alignment' => Jc::START,  'spaceBefore' => 0, 'spaceAfter' => 0];

        $tableStyle = [
            'borderTopSize'     => 6, 'borderTopColor'     => self::BLACK,
            'borderLeftSize'    => 6, 'borderLeftColor'    => self::BLACK,
            'borderRightSize'   => 6, 'borderRightColor'   => self::BLACK,
            'borderBottomSize'  => 6, 'borderBottomColor'  => self::BLACK,
            'borderInsideHSize' => 6, 'borderInsideHColor' => self::BLACK,
            'borderInsideVSize' => 6, 'borderInsideVColor' => self::BLACK,
        ];

        $table = $section->addTable($tableStyle);

        // ── Header row 1 ───────────────────────────────────────────────────
        $table->addRow();
        $bgO = ['bgColor' => self::ORANGE_BG];

        // Cells that span 2 header rows (rowspan)
        $rsCells = [
            [$cols[0],  'លរ.'],
            [$cols[1],  'កូដទីតាំង'],
            [$cols[2],  'ឃុំ'],
            [$cols[3],  'ស្រុក'],
            [$cols[4],  'កាលបរិច្ឆេទ'],
            [$cols[5],  'ទីតាំងសំណង់'],
        ];
        foreach ($rsCells as [$w, $txt]) {
            $c = $table->addCell($w, array_merge($bgO, ['vMerge' => 'restart', 'valign' => 'center']));
            $c->addText($txt, $headerFont, $centerPara);
        }

        // "អ្នកទទួលផល" colspan=2
        $c = $table->addCell($cols[6] + $cols[7], array_merge($bgO, ['gridSpan' => 2, 'valign' => 'center']));
        $c->addText('អ្នកទទួលផល', $headerFont, $centerPara);

        // Operators rowspan
        $c = $table->addCell($cols[8], array_merge($bgO, ['vMerge' => 'restart', 'valign' => 'center']));
        $c->addText('ចំនួន ប្រតិបត្តិករ', $headerFont, $centerPara);

        // "កម្មវិធីសាលារៀន" colspan=2
        $c = $table->addCell($cols[9] + $cols[10], array_merge($bgO, ['gridSpan' => 2, 'valign' => 'center']));
        $c->addText('កម្មវិធីសាលារៀន', $headerFont, $centerPara);

        // Status rowspan
        $c = $table->addCell($cols[11], array_merge($bgO, ['vMerge' => 'restart', 'valign' => 'center']));
        $c->addText('ស្ថានីយសកម្ម', $headerFont, $centerPara);

        // ── Header row 2 ───────────────────────────────────────────────────
        $table->addRow();

        // Continue the rowspan cells (cols 0–5)
        foreach ([$cols[0], $cols[1], $cols[2], $cols[3], $cols[4], $cols[5]] as $w) {
            $table->addCell($w, array_merge($bgO, ['vMerge' => 'continue']));
        }

        // Sub-headers for "អ្នកទទួលផល"
        $c = $table->addCell($cols[6], array_merge($bgO, ['valign' => 'center']));
        $c->addText('ចំនួន', $headerFont, $centerPara);
        $c = $table->addCell($cols[7], array_merge($bgO, ['valign' => 'center']));
        $c->addText('ភាគរយ', $headerFont, $centerPara);

        // Continue operators rowspan
        $table->addCell($cols[8], array_merge($bgO, ['vMerge' => 'continue']));

        // Sub-headers for "កម្មវិធីទឹកសាលារៀន"
        $c = $table->addCell($cols[9], array_merge($bgO, ['valign' => 'center']));
        $c->addText('ចំនួនសាលា', $headerFont, $centerPara);
        $c = $table->addCell($cols[10], array_merge($bgO, ['valign' => 'center']));
        $c->addText('ចំនួនសិស្ស', $headerFont, $centerPara);

        // Continue status rowspan
        $table->addCell($cols[11], array_merge($bgO, ['vMerge' => 'continue']));

        // ── Data rows ──────────────────────────────────────────────────────
        foreach ($rows as $row) {
            $table->addRow();

            $c = $table->addCell($cols[0], ['valign' => 'top']);
            $c->addText((string) ($row['index'] ?? ''), $dataFont, $centerPara);

            $c = $table->addCell($cols[1], ['valign' => 'top']);
            $c->addText((string) ($row['id_site'] ?? ''), $dataFont, $centerPara);

            $c = $table->addCell($cols[2], ['valign' => 'top']);
            $c->addText((string) ($row['commune'] ?? ''), $dataFont, $leftPara);

            $c = $table->addCell($cols[3], ['valign' => 'top']);
            $c->addText((string) ($row['district'] ?? ''), $dataFont, $leftPara);

            $c = $table->addCell($cols[4], ['valign' => 'top']);
            $c->addText((string) ($row['starting_date'] ?? ''), $dataFont, $centerPara);

            $c = $table->addCell($cols[5], ['valign' => 'top']);
            $c->addText((string) ($row['land_of_kiosk'] ?? ''), $dataFont, $leftPara);

            $c = $table->addCell($cols[6], ['valign' => 'top']);
            $c->addText($this->numText($row['beneficiaries'] ?? null), $dataFont, $rightPara);

            $c = $table->addCell($cols[7], ['valign' => 'top']);
            $c->addText($this->pctText($row['beneficiaries_pct'] ?? null), $dataFont, $rightPara);

            $c = $table->addCell($cols[8], ['valign' => 'top']);
            $c->addText($this->numText($row['operators'] ?? null), $dataFont, $rightPara);

            $c = $table->addCell($cols[9], ['valign' => 'top']);
            $c->addText($this->numText($row['nb_schools'] ?? null), $dataFont, $rightPara);

            $c = $table->addCell($cols[10], ['valign' => 'top']);
            $c->addText($this->numText($row['nb_students'] ?? null), $dataFont, $rightPara);

            $c = $table->addCell($cols[11], ['valign' => 'top']);
            $c->addText((string) ($row['status'] ?? ''), $dataFont, $centerPara);
        }
    }

    // ─── Helpers ─────────────────────────────────────────────────────────────

    private function addMultilineText(Section $section, string $text, array $font, array $para): void
    {
        if ($text === '') return;
        foreach (explode("\n", $text) as $line) {
            $section->addText($line, $font ?: null, $para);
        }
    }

    private function noBorderCell(): array
    {
        return [
            'borderTopSize'    => 0, 'borderTopColor'    => self::WHITE,
            'borderBottomSize' => 0, 'borderBottomColor' => self::WHITE,
            'borderLeftSize'   => 0, 'borderLeftColor'   => self::WHITE,
            'borderRightSize'  => 0, 'borderRightColor'  => self::WHITE,
        ];
    }

    private function numText(mixed $val): string
    {
        if ($val === null || $val === '') return '';
        $int = filter_var($val, FILTER_VALIDATE_INT);
        if ($int === false) return (string) $val;
        return number_format($int, 0, '.', ' ');
    }

    private function pctText(mixed $val): string
    {
        if ($val === null || $val === '') return '';
        $float = filter_var($val, FILTER_VALIDATE_FLOAT);
        if ($float === false) return (string) $val;
        return number_format($float, 1, '.', '') . '%';
    }
}
