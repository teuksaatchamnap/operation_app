/**
 * Cambodian Public Holidays
 * Note: Some holidays follow the lunar calendar and may vary by year
 */

// Fixed date holidays (same date every year)
const fixedHolidays = [
    { month: 1, day: 1, name: "International New Year Day" },
    { month: 1, day: 7, name: "Victory Day over the Genocidal Regime" },
    { month: 3, day: 8, name: "International Women's Day" },
    { month: 5, day: 1, name: "International Labour Day" },
    { month: 5, day: 13, name: "King's Birthday" },
    { month: 5, day: 14, name: "King's Birthday" },
    { month: 6, day: 18, name: "Queen Mother's Birthday" },
    { month: 9, day: 24, name: "Constitution Day" },
    { month: 10, day: 15, name: "Commemoration Day of King Father Norodom Sihanouk" },
    { month: 10, day: 29, name: "Coronation Day" },
    { month: 11, day: 9, name: "Independence Day" },
];

// Lunar calendar holidays (approximate dates - these vary by year)
// These are approximate dates for common years, you may want to update these annually
const lunarHolidays = {
    2024: [
        { month: 2, day: 10, name: "Lunar New Year" },
        { month: 2, day: 11, name: "Lunar New Year" },
        { month: 2, day: 12, name: "Lunar New Year" },
        { month: 4, day: 13, name: "Khmer New Year" },
        { month: 4, day: 14, name: "Khmer New Year" },
        { month: 4, day: 15, name: "Khmer New Year" },
        { month: 5, day: 22, name: "Royal Ploughing Ceremony" },
        { month: 5, day: 23, name: "Visak Bochea Day" },
        { month: 9, day: 16, name: "Pchum Ben Day" },
        { month: 9, day: 17, name: "Pchum Ben Day" },
        { month: 9, day: 18, name: "Pchum Ben Day" },
        { month: 11, day: 14, name: "Water Festival" },
        { month: 11, day: 15, name: "Water Festival" },
        { month: 11, day: 16, name: "Water Festival" },
    ],
    2025: [
        { month: 1, day: 29, name: "Lunar New Year" },
        { month: 1, day: 30, name: "Lunar New Year" },
        { month: 1, day: 31, name: "Lunar New Year" },
        { month: 4, day: 14, name: "Khmer New Year" },
        { month: 4, day: 15, name: "Khmer New Year" },
        { month: 4, day: 16, name: "Khmer New Year" },
        { month: 5, day: 11, name: "Royal Ploughing Ceremony" },
        { month: 5, day: 12, name: "Visak Bochea Day" },
        { month: 10, day: 4, name: "Pchum Ben Day" },
        { month: 10, day: 5, name: "Pchum Ben Day" },
        { month: 10, day: 6, name: "Pchum Ben Day" },
        { month: 11, day: 4, name: "Water Festival" },
        { month: 11, day: 5, name: "Water Festival" },
        { month: 11, day: 6, name: "Water Festival" },
    ],
    2026: [
        { month: 2, day: 17, name: "Lunar New Year" },
        { month: 2, day: 18, name: "Lunar New Year" },
        { month: 2, day: 19, name: "Lunar New Year" },
        { month: 4, day: 14, name: "Khmer New Year" },
        { month: 4, day: 15, name: "Khmer New Year" },
        { month: 4, day: 16, name: "Khmer New Year" },
        { month: 5, day: 1, name: "Royal Ploughing Ceremony" },
        { month: 5, day: 31, name: "Visak Bochea Day" },
        { month: 9, day: 23, name: "Pchum Ben Day" },
        { month: 9, day: 24, name: "Pchum Ben Day" },
        { month: 9, day: 25, name: "Pchum Ben Day" },
        { month: 11, day: 23, name: "Water Festival" },
        { month: 11, day: 24, name: "Water Festival" },
        { month: 11, day: 25, name: "Water Festival" },
    ],
    2027: [
        { month: 2, day: 6, name: "Lunar New Year" },
        { month: 2, day: 7, name: "Lunar New Year" },
        { month: 2, day: 8, name: "Lunar New Year" },
        { month: 4, day: 14, name: "Khmer New Year" },
        { month: 4, day: 15, name: "Khmer New Year" },
        { month: 4, day: 16, name: "Khmer New Year" },
        { month: 5, day: 20, name: "Royal Ploughing Ceremony" },
        { month: 5, day: 19, name: "Visak Bochea Day" },
        { month: 10, day: 12, name: "Pchum Ben Day" },
        { month: 10, day: 13, name: "Pchum Ben Day" },
        { month: 10, day: 14, name: "Pchum Ben Day" },
        { month: 11, day: 12, name: "Water Festival" },
        { month: 11, day: 13, name: "Water Festival" },
        { month: 11, day: 14, name: "Water Festival" },
    ],
};

/**
 * Check if a given date is a Cambodian public holiday
 * @param {Date} date - The date to check
 * @returns {Object|null} - Returns holiday object with name if it's a holiday, null otherwise
 */
export function isCambodianHoliday(date) {
    const month = date.getMonth() + 1; // JavaScript months are 0-indexed
    const day = date.getDate();
    const year = date.getFullYear();

    // Check fixed holidays
    const fixedHoliday = fixedHolidays.find(
        (h) => h.month === month && h.day === day
    );
    if (fixedHoliday) {
        return { name: fixedHoliday.name, type: 'fixed' };
    }

    // Check lunar holidays for the specific year
    const yearHolidays = lunarHolidays[year];
    if (yearHolidays) {
        const lunarHoliday = yearHolidays.find(
            (h) => h.month === month && h.day === day
        );
        if (lunarHoliday) {
            return { name: lunarHoliday.name, type: 'lunar' };
        }
    }

    return null;
}

/**
 * Get the name of the holiday for a given date
 * @param {Date} date - The date to check
 * @returns {string|null} - Returns holiday name if it's a holiday, null otherwise
 */
export function getHolidayName(date) {
    const holiday = isCambodianHoliday(date);
    return holiday ? holiday.name : null;
}
