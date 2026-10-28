<template>
    <div class="header-bar px-6 py-3 d-flex align-center justify-space-between">
        <div class="d-flex align-center ga-3">
            <!-- Logo mark -->
            <div class="logo-mark d-flex align-center justify-center">
                <v-icon color="white" size="28">mdi-water-pump</v-icon>
            </div>
            <div>
                <div class="text-h6 font-weight-bold text-white">TeukSaat 1001</div>
                <div class="text-caption text-white" style="opacity:.75">Technical Management System</div>
            </div>
        </div>

        <div class="d-flex align-center ga-2">
            <v-chip color="white" variant="outlined" size="small" prepend-icon="mdi-circle" class="status-chip">
                Live
            </v-chip>
            <v-btn icon variant="text" color="white" size="small">
                <v-icon>mdi-bell-outline</v-icon>
            </v-btn>
            <v-avatar color="white" size="34">
                <v-icon color="primary">mdi-account</v-icon>
            </v-avatar>
        </div>
    </div>
</template>

<style scoped>
.header-bar {
    background: linear-gradient(135deg, #1565C0 0%, #0D47A1 60%, #1976D2 100%);
    box-shadow: 0 2px 12px rgba(21, 101, 192, 0.3);
}

.logo-mark {
    width: 46px;
    height: 46px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(4px);
}

.status-chip {
    animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {

    0%,
    100% {
        opacity: 1;
    }

    50% {
        opacity: 0.6;
    }
}
</style>
