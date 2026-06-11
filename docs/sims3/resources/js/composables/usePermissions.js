import { computed } from "vue";
import { useStore } from "vuex";

export function usePermissions() {
    const store = useStore();

    const isCashierAdmin = computed(() => {
        const user = store.state.user;
        return !!(
            user &&
            user.permissions &&
            user.permissions.includes("cashier_admin")
        );
    });

    return {
        isCashierAdmin,
    };
}
