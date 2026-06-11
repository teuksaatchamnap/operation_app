export function useCashierNotifications() {
    const fetchNotificationMessage = async (key) => {
        try {
            const response = await window.axios.get('/api/cashier-notifications');
            const notification = response.data.find(n => n.key === key);
            if (notification) {
                return notification;
            }
        } catch (error) {
            console.error('Error fetching notification message:', error);
        }
        return null;
    };

    return {
        fetchNotificationMessage,
    };
}
