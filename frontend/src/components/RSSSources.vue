<template>
    <div v-if="journals.length > 0" class="rss-all-items">
        <div v-for="journal in journals" :key="journal.source" class="rss-item">
            <a :href="journal.feed" target="_blank">{{ journal.source }}</a>
        </div>
    </div>
</template>

<script setup lang="ts">
import axios from 'axios';
import { ref, onMounted } from 'vue'

interface RSSSource {
    source: string;
    feed: string;
}

interface LLM_Prompt {
    base_url: string;
    prompt: string;
    model_name: string;
}

let journals = ref<RSSSource[]>([]);
let llm_prompts = ref("");

async function fetchRSSSources() {
    try {
        const response = await axios.get<RSSSource[]>('/api/rss/sources');
        journals.value = response.data;
    } catch (error) {
        console.error('Error fetching RSS sources:', error);
    }
}

async function fetchLLMPrompts() {
    try {
        const response = await axios.get<LLM_Prompt>('/api/rss/llm_prompt');
        llm_prompts.value = response.data.prompt;
    } catch (error) {
        console.error('Error fetching LLM prompts:', error);
    }
}

onMounted(async () => {
    await fetchRSSSources();
    await fetchLLMPrompts();
})

</script>
<style scoped>
.rss-item {
    margin: 10px 0;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 10px;
}

.rss-all-items {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-around;
}

</style>