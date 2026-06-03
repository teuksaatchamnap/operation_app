import { ref, watch } from "vue";

const STORAGE_KEY = "app-currency";

function loadCurrency() {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored === "riel" || stored === "usd") return stored;
    } catch {}
    return "riel";
}

const currency = ref(loadCurrency());

watch(currency, (val) => {
    try {
        localStorage.setItem(STORAGE_KEY, val);
    } catch {}
});

const KHR_TO_USD = 4000;

export function formatCurrency(value) {
    if (value === null || value === undefined) return "-";
    if (currency.value === "usd") {
        const converted = value / KHR_TO_USD;
        return (
            "$" +
            converted.toLocaleString("en-US", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            })
        );
    }
    return "៛" + Number(value).toLocaleString("en-US", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    });
}

export function useCurrency() {
    return { currency, formatCurrency, KHR_TO_USD };
}
