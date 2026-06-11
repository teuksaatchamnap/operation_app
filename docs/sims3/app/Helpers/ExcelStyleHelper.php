<?php

namespace App\Helpers;

use PhpOffice\PhpSpreadsheet\Style\Alignment;
use PhpOffice\PhpSpreadsheet\Style\Border;
use PhpOffice\PhpSpreadsheet\Style\Fill;
use PhpOffice\PhpSpreadsheet\Style\NumberFormat;
use PhpOffice\PhpSpreadsheet\Worksheet\Worksheet;

/**
 * Helper centralisant les styles Excel récurrents dans tous les exports.
 *
 * Objectif : éviter de redéfinir les mêmes tableaux de style dans chaque Export.
 * Quand un format doit changer (couleur corporate, format monétaire…), on le fait ici
 * et TOUS les rapports sont mis à jour automatiquement.
 *
 * Utilisation :
 *   ExcelStyleHelper::applyHeaderStyle($ws, 'A1:Z1', ExcelStyleHelper::COLOR_BLUE);
 *   ExcelStyleHelper::setNumberFormat($ws, 'C2:C100', ExcelStyleHelper::FMT_THOUSANDS);
 */
class ExcelStyleHelper
{
    // ──────────────── Couleurs corporate ────────────────
    /** Bleu foncé — titres YTD / sections ventes */
    public const COLOR_BLUE         = '0070C0';
    /** Vert foncé — titres indicateurs mensuels */
    public const COLOR_GREEN        = '00B050';
    /** Orange — sections management */
    public const COLOR_ORANGE       = 'ED7D31';
    /** Rouge — dépenses, alertes */
    public const COLOR_RED          = 'FE6262';
    /** Gris — cellules vides, historique */
    public const COLOR_GREY         = 'C0C0C0';
    /** Gris clair — arrière-plan info site */
    public const COLOR_LIGHT_GREY   = 'DCE6F1';
    /** Cyan clair — arrière-plan info site */
    public const COLOR_CYAN         = 'DAEEF3';
    /** Vert clair — commentaires */
    public const COLOR_LIGHT_GREEN  = 'C4E59F';
    /** Bleu clair — indicateurs */
    public const COLOR_LIGHT_BLUE   = '8DB4E2';
    /** Rouge clair — dépenses */
    public const COLOR_LIGHT_RED    = 'DA9694';
    /** Jaune — titres spéciaux */
    public const COLOR_YELLOW       = 'FFFF00';

    // ──────────────── Formats numériques ────────────────
    /** Milliers avec séparateur espace : 1 234 567 */
    public const FMT_THOUSANDS      = '#,##0';
    /** Milliers + $ : 1 234 567 $ */
    public const FMT_THOUSANDS_USD  = '#,##0 $';
    /** Riels avec symbole khmer : ៛1,234,567 */
    public const FMT_RIEL           = '៛#,##0';
    /** Pourcentage simple : 85% */
    public const FMT_PERCENT        = '0%';
    /** Pourcentage signé : +12% / -5% */
    public const FMT_PERCENT_SIGNED = '+0%;-0%';
    /** Décimales : 1 234.56 */
    public const FMT_DECIMAL        = '#,##0.00';
    /** Date mois-année : Jan-2025 */
    public const FMT_DATE_MON_YY    = 'mmm-yy';
    /** Date YYYY-MM */
    public const FMT_DATE_YYYY_MM   = 'yyyy-mm';
    /** Date MM/YYYY */
    public const FMT_DATE_MM_YYYY   = 'mm/yyyy';
    /** Date complète */
    public const FMT_DATE_FULL      = 'yyyy/mm/dd';

    /**
     * Applique un style d'en-tête (fond coloré, texte blanc gras, centré, bordure) sur une plage.
     *
     * @param  Worksheet  $ws       Feuille cible.
     * @param  string     $range    Plage Excel (ex : 'A1:Z1').
     * @param  string     $bgColor  Code hex sans # (ex : '0070C0').
     * @param  string     $fontColor  Code hex police (défaut blanc).
     */
    public static function applyHeaderStyle(
        Worksheet $ws,
        string $range,
        string $bgColor,
        string $fontColor = 'FFFFFF'
    ): void {
        $ws->getStyle($range)->applyFromArray([
            'font' => [
                'bold'  => true,
                'color' => ['argb' => "FF{$fontColor}"],
            ],
            'fill' => [
                'fillType'   => Fill::FILL_SOLID,
                'startColor' => ['argb' => "FF{$bgColor}"],
            ],
            'alignment' => [
                'horizontal' => Alignment::HORIZONTAL_CENTER,
                'vertical'   => Alignment::VERTICAL_CENTER,
                'wrapText'   => true,
            ],
            'borders' => [
                'allBorders' => [
                    'borderStyle' => Border::BORDER_THIN,
                ],
            ],
        ]);
    }

    /**
     * Applique un style "info site" (fond bleu clair, bordure épaisse).
     */
    public static function applySiteInfoStyle(Worksheet $ws, string $range): void
    {
        $ws->getStyle($range)->applyFromArray([
            'fill' => [
                'fillType'   => Fill::FILL_SOLID,
                'startColor' => ['argb' => 'FF' . self::COLOR_LIGHT_GREY],
            ],
            'borders' => [
                'allBorders' => [
                    'borderStyle' => Border::BORDER_MEDIUM,
                ],
            ],
        ]);
    }

    /**
     * Applique un format numérique à une plage entière.
     *
     * @param  Worksheet  $ws
     * @param  string     $range   Plage Excel.
     * @param  string     $format  Constante FMT_* de cette classe.
     */
    public static function setNumberFormat(Worksheet $ws, string $range, string $format): void
    {
        $ws->getStyle($range)->getNumberFormat()->setFormatCode($format);
    }

    /**
     * Applique un fond gris aux cellules vides d'une plage (post-écriture).
     * Parcourt chaque cellule ; si elle est vide, met un fond gris.
     *
     * @param  Worksheet  $ws
     * @param  string     $range
     */
    public static function greyOutEmptyCells(Worksheet $ws, string $range): void
    {
        $cells = $ws->rangeToArray($range, null, false, false);
        [$startCol, $startRow] = \PhpOffice\PhpSpreadsheet\Cell\Coordinate::coordinateFromString(
            explode(':', $range)[0]
        );
        $colIndex = \PhpOffice\PhpSpreadsheet\Cell\Coordinate::columnIndexFromString($startCol);

        foreach ($cells as $rowIdx => $row) {
            foreach ($row as $cellIdx => $value) {
                if ($value === null || $value === '' || $value === 0) {
                    $cellCoord = \PhpOffice\PhpSpreadsheet\Cell\Coordinate::stringFromColumnIndex($colIndex + $cellIdx)
                        . ($startRow + $rowIdx);
                    $ws->getStyle($cellCoord)->getFill()
                        ->setFillType(Fill::FILL_SOLID)
                        ->getStartColor()->setARGB('FF' . self::COLOR_GREY);
                }
            }
        }
    }

    /**
     * Applique bold + bordure à une plage (lignes de totaux typiquement).
     */
    public static function applyTotalRowStyle(Worksheet $ws, string $range): void
    {
        $ws->getStyle($range)->applyFromArray([
            'font' => ['bold' => true],
            'borders' => [
                'allBorders' => [
                    'borderStyle' => Border::BORDER_THIN,
                ],
            ],
        ]);
    }

    /**
     * Définit les largeurs de colonnes en batch.
     *
     * @param  Worksheet  $ws
     * @param  array      $widths  Tableau associatif ['A' => 12, 'B' => 20, …]
     */
    public static function setColumnWidths(Worksheet $ws, array $widths): void
    {
        foreach ($widths as $col => $width) {
            $ws->getColumnDimension($col)->setWidth($width);
        }
    }
}
