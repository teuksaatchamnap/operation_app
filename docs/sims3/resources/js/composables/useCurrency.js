export function useCurrency() {
    const formatKHR = (amount) => {
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "KHR",
            maximumFractionDigits: 0,
            currencyDisplay: "symbol",
        })
            .format(amount)
            .replace("KHR", "៛")
            .trim();
    };

    return {
        formatKHR,
    };
}
