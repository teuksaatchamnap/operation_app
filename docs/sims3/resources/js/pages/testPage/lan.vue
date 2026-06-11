<template>
    <div class="container mx-auto p-4">
        <h1 class="text-2xl font-bold mb-4">Language Switch Example</h1>

        <!-- v-select for language selection -->
        <v-select v-model="selectedLanguage" :options="languages" label="name" placeholder="Select Language"
            class="mb-4" @update:modelValue="fetchData"></v-select>

        <!-- Display data based on selected language -->
        <div v-if="data" class="bg-gray-100 p-4 rounded">
            <h2 class="text-xl font-semibold">{{ data.title }}</h2>
            <p>{{ data.description }}</p>
        </div>
        <div v-else-if="loading" class="text-center">Loading...</div>
        <div v-else class="text-red-500">No data available</div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import vSelect from 'vue-select';
import 'vue-select/dist/vue-select.css';

// Language options
const languages = [
    { code: 'en', name: 'English' },
    { code: 'km', name: 'Khmer' }
];

// Reactive state
const selectedLanguage = ref(null);
const data = ref(null);
const loading = ref(false);

// Fetch data based on selected language
const fetchData = async () => {
    if (!selectedLanguage.value) return;

    loading.value = true;
    try {
        const response = await axios.get(`/api/content/${selectedLanguage.value.code}`);
        data.value = response.data;
    } catch (error) {
        console.error('Error fetching data:', error);
        data.value = null;
    } finally {
        loading.value = false;
    }
};

// Fetch initial data when component mounts
onMounted(() => {
    selectedLanguage.value = languages[0]; // Default to English
    fetchData();
});
</script>

<style scoped>
/* Add custom styles if needed */
.container {
    max-width: 600px;
}
</style>