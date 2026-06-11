<?php

namespace App\Helpers;

use Carbon\Carbon;

/**
 * Khmer (Chhankitek) lunar date formatter.
 *
 * Returns the traditional Khmer lunar date for a Gregorian date, e.g.:
 *   ថ្ងៃពុធ ១៤ កើត ខែពិសាខ ឆ្នាំមមី អដ្ឋស័ក ព.ស ២៥៦៩
 *
 * The implementation is based on the Chhankitek calendar using the astronomical
 * synodic-month approximation for the lunar day, and the standard solar-month
 * mapping for the lunar month name. Animal/Sak/BE follow the post-Khmer-New-Year
 * convention (cycle changes mid-April).
 */
class KhmerLunarDate
{
    private const LUNAR_MONTHS = [
        'មិគសិរ', 'បុស្ស', 'មាឃ', 'ផល្គុន',
        'ចេត្រ', 'ពិសាខ', 'ជេស្ឋ', 'អាសាឍ',
        'ស្រាពណ៍', 'ភទ្របទ', 'អស្សុជ', 'កត្តិក',
    ];

    private const ANIMAL_YEARS = [
        'ជូត', 'ឆ្លូវ', 'ខាល', 'ថោះ', 'រោង', 'ម្សាញ់',
        'មមី', 'មមែ', 'វក', 'រកា', 'ច', 'កុរ',
    ];

    private const SAK_NAMES = [
        'សំរឹទ្ធិស័ក', 'ឯកស័ក', 'ទោស័ក', 'ត្រីស័ក', 'ចត្វាស័ក',
        'បញ្ចស័ក', 'ឆស័ក', 'សប្តស័ក', 'អដ្ឋស័ក', 'នព្វស័ក',
    ];

    private const WEEKDAYS = [
        'អាទិត្យ', 'ច័ន្ទ', 'អង្គារ', 'ពុធ', 'ព្រហស្បតិ៍', 'សុក្រ', 'សៅរ៍',
    ];

    private const SYNODIC_MONTH = 29.530588853;

    // Reference new moon: 2000-01-06 at 18:14 UT  →  JDN ≈ 2451550.26
    private const NEW_MOON_REFERENCE_JD = 2451550.26;

    // Khmer New Year cutoff (animal/Sak/BE cycle rollover): April 14
    private const KH_NEW_YEAR_MONTH = 4;
    private const KH_NEW_YEAR_DAY   = 14;

    public function format(Carbon $date): string
    {
        $info = $this->compute($date);

        return sprintf(
            'ថ្ងៃ%s %s %s ខែ%s ឆ្នាំ%s %s ព.ស %s',
            $info['weekday'],
            $this->toKhmerNumber($info['lunar_day']),
            $info['phase'],
            $info['lunar_month'],
            $info['animal'],
            $info['sak'],
            $this->toKhmerNumber($info['be_year'])
        );
    }

    public function compute(Carbon $date): array
    {
        $jd  = $this->gregorianToJD($date->year, $date->month, $date->day);
        $dow = ($jd + 1) % 7;

        // Lunar day & phase
        $newMoonJd   = $this->newMoonOnOrBefore($jd);
        $daysSince   = (int) floor($jd - $newMoonJd);
        $lunarDay    = $daysSince + 1;
        if ($lunarDay <= 15) {
            $phase    = 'កើត';
            $khDay    = $lunarDay;
        } else {
            $phase    = 'រោច';
            $khDay    = $lunarDay - 15;
        }

        // Lunar month name from the new moon's Gregorian date
        $newMoonDate  = $this->jdToGregorian($newMoonJd);
        $lunarMonthIx = $this->lunarMonthIndex($newMoonDate);

        // BE year, animal, Sak — rolls over on Khmer New Year
        $afterKny = $this->isAfterKhmerNewYear($date);
        $cycleYearAd = $afterKny ? $date->year : ($date->year - 1);

        $beYear     = $date->year + 543;
        $animalIdx  = (($cycleYearAd - 4) % 12 + 12) % 12;
        $sakIdx     = (($cycleYearAd - 638) % 10 + 10) % 10;

        return [
            'weekday'     => self::WEEKDAYS[$dow],
            'lunar_day'   => $khDay,
            'phase'       => $phase,
            'lunar_month' => self::LUNAR_MONTHS[$lunarMonthIx],
            'animal'      => self::ANIMAL_YEARS[$animalIdx],
            'sak'         => self::SAK_NAMES[$sakIdx],
            'be_year'     => $beYear,
        ];
    }

    private function gregorianToJD(int $year, int $month, int $day): int
    {
        if ($month <= 2) {
            $year  -= 1;
            $month += 12;
        }
        $a = intdiv($year, 100);
        $b = 2 - $a + intdiv($a, 4);
        return (int) (floor(365.25 * ($year + 4716))
            + floor(30.6001 * ($month + 1))
            + $day + $b - 1524);
    }

    private function jdToGregorian(float $jd): array
    {
        $z = (int) floor($jd + 0.5);
        $a = $z;
        if ($z >= 2299161) {
            $alpha = (int) floor(($z - 1867216.25) / 36524.25);
            $a = $z + 1 + $alpha - intdiv($alpha, 4);
        }
        $b = $a + 1524;
        $c = (int) floor(($b - 122.1) / 365.25);
        $d = (int) floor(365.25 * $c);
        $e = (int) floor(($b - $d) / 30.6001);
        $day   = $b - $d - (int) floor(30.6001 * $e);
        $month = $e < 14 ? $e - 1 : $e - 13;
        $year  = $month > 2 ? $c - 4716 : $c - 4715;
        return ['year' => $year, 'month' => $month, 'day' => $day];
    }

    private function newMoonOnOrBefore(int $jd): float
    {
        $cycles = floor(($jd - self::NEW_MOON_REFERENCE_JD) / self::SYNODIC_MONTH);
        $nm     = self::NEW_MOON_REFERENCE_JD + $cycles * self::SYNODIC_MONTH;
        while (floor($nm) > $jd) {
            $nm -= self::SYNODIC_MONTH;
        }
        while (floor($nm + self::SYNODIC_MONTH) <= $jd) {
            $nm += self::SYNODIC_MONTH;
        }
        return $nm;
    }

    /**
     * Map a new-moon Gregorian date to its Khmer lunar month index.
     * Each lunar month "starts" on a new moon that falls within roughly
     * a one-month solar window. The windows below are the traditional
     * Cambodian correspondences.
     */
    private function lunarMonthIndex(array $nm): int
    {
        $m = $nm['month'];
        $d = $nm['day'];

        // Window start dates (month, day) for each lunar month name.
        // Mikasir (0): Nov 14 – Dec 13
        // Boss    (1): Dec 14 – Jan 13
        // Meak    (2): Jan 14 – Feb 12
        // Phalkun (3): Feb 13 – Mar 13
        // Chet    (4): Mar 14 – Apr 13
        // Pisak   (5): Apr 14 – May 13
        // Jeth    (6): May 14 – Jun 13
        // Asad    (7): Jun 14 – Jul 13
        // Srep    (8): Jul 14 – Aug 12
        // Bhad    (9): Aug 13 – Sep 12
        // Assoj  (10): Sep 13 – Oct 13
        // Kattek (11): Oct 14 – Nov 13
        $windows = [
            [11, 14, 0],
            [12, 14, 1],
            [1,  14, 2],
            [2,  13, 3],
            [3,  14, 4],
            [4,  14, 5],
            [5,  14, 6],
            [6,  14, 7],
            [7,  14, 8],
            [8,  13, 9],
            [9,  13, 10],
            [10, 14, 11],
        ];

        // Determine the lunar month by finding which window the new moon's (m,d) falls into.
        // Windows wrap around the year, so compare against each start (inclusive) and the next start.
        $idx = 11; // default to Kattek
        foreach ($windows as $i => [$wm, $wd, $monthIdx]) {
            $next = $windows[($i + 1) % count($windows)];
            if ($this->dateInRange($m, $d, $wm, $wd, $next[0], $next[1])) {
                $idx = $monthIdx;
                break;
            }
        }
        return $idx;
    }

    private function dateInRange(int $m, int $d, int $sm, int $sd, int $em, int $ed): bool
    {
        $val   = $m * 100 + $d;
        $start = $sm * 100 + $sd;
        $end   = $em * 100 + $ed;
        if ($start <= $end) {
            return $val >= $start && $val < $end;
        }
        // Window wraps across year boundary
        return $val >= $start || $val < $end;
    }

    private function isAfterKhmerNewYear(Carbon $date): bool
    {
        if ($date->month > self::KH_NEW_YEAR_MONTH) return true;
        if ($date->month < self::KH_NEW_YEAR_MONTH) return false;
        return $date->day >= self::KH_NEW_YEAR_DAY;
    }

    private function toKhmerNumber(int|string $n): string
    {
        return strtr((string) $n, [
            '0' => '០', '1' => '១', '2' => '២', '3' => '៣', '4' => '៤',
            '5' => '៥', '6' => '៦', '7' => '៧', '8' => '៨', '9' => '៩',
        ]);
    }
}
