<script setup lang="ts">
import RSSTable from './components/RSSTable.vue';
import { ref } from 'vue';
// import RSSSources from './components/RSSSources.vue';

const BASE_URL = window.location.pathname.replace(/\/+$/, '');
const RSS_LLM_PROMPT_API = ref(`${BASE_URL}/api/rss/llm_prompt`);
const RSS_SOURCES_API = ref(`${BASE_URL}/api/rss/sources`);

</script>

<template>
  <div>
    <h1>Journal RSS Rater</h1>
  </div>

  <div>
    <p>
    <blockquote><a :href="RSS_LLM_PROMPT_API">See Prompts</a></blockquote>
    <blockquote><a :href="RSS_SOURCES_API">See RSS Sources</a></blockquote>
    </p>
  </div>

  <!-- <div>
    <RSSSources />
  </div> -->

  <div>
    <RSSTable />
  </div>
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
