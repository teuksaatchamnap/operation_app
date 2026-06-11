import { useI18n } from "vue-i18n";

const getLocale = () => {
    const { locale } = useI18n();
    const localeMap = {
        en: "en-US",
        kh: "km-KH",
    };
    return localeMap[locale.value] || "en-US";
};

const khmerMonths = [
    "មករា", "កុម្ភៈ", "មីនា", "មេសា", "ឧសភា", "មិថុនា",
    "កក្កដា", "សីហា", "កញ្ញា", "តុលា", "វិច្ឆិកា", "ធ្នូ"
];

const khmerWeekdays = [
    "អាទិត្យ", "ច័ន្ទ", "អង្គារ", "ពុធ", "ព្រហស្បតិ៍", "សុក្រ", "សៅរ៍"
];

const formatKhmerDate = (date, includeWeekday = true) => {
    const day = date.getDate();
    const month = khmerMonths[date.getMonth()];
    const year = date.getFullYear();
    const weekday = khmerWeekdays[date.getDay()];
    
    if (includeWeekday) {
        return `${weekday}, ${day} ${month} ${year}`;
    }
    return `${day} ${month} ${year}`;
};

export const formatDateForDisplay = (dateString) => {
    if (!dateString) return "";
    const locale = getLocale();
    const date = new Date(dateString);
    
    // Use custom formatting for Khmer
    if (locale === "km-KH") {
        return formatKhmerDate(date, true);
    }
    
    // Use native formatting for other locales
    return date.toLocaleDateString(locale, {
        year: "numeric",
        month: "short",
        day: "numeric",
        weekday: "long",
    });
};

export const formatDateForDisplaySimple = (dateString) => {
    if (!dateString) return "";
    const locale = getLocale();
    const date = new Date(dateString);
    
    // Use custom formatting for Khmer
    if (locale === "km-KH") {
        return formatKhmerDate(date, false);
    }
    
    // Use native formatting for other locales
    return date.toLocaleDateString(locale, {
        year: "numeric",
        month: "short",
        day: "numeric",
    });
};

export const parseDateToUTC = (date) => {
    if (!date) return null;
    if (typeof date === "string") {
        const parts = date.split("-");
        return new Date(
            Date.UTC(
                parseInt(parts[0], 10),
                parseInt(parts[1], 10) - 1,
                parseInt(parts[2], 10)
            )
        );
    }
    const d = new Date(date);
    return new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
};

export const formatDateRange = (startDate, endDate) => {
    if (startDate && endDate) {
        const start = parseDateToUTC(startDate);
        const end = parseDateToUTC(endDate);
        const options = {
            month: "short",
            day: "numeric",
            year: "numeric",
            timeZone: "UTC",
        };
        return `${start.toLocaleDateString(
            undefined,
            options
        )} - ${end.toLocaleDateString(undefined, options)}`;
    }
    return "";
};

export const calculateDaysBetween = (startDate, endDate) => {
    if (startDate && endDate) {
        const start = parseDateToUTC(startDate);
        const end = parseDateToUTC(endDate);
        const diffTime = Math.abs(end - start);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
        return diffDays;
    }
    return 0;
};
