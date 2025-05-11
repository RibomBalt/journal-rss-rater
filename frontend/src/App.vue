<script setup lang="ts">
import RSSTable from './components/RSSTable.vue';
import RSSSources from './components/RSSSources.vue';
</script>

<template>
  <div>
    <h1>Journal RSS Rater</h1>
  </div>

  <div>
    <p>
    <blockquote><a href="/api/rss/llm_prompt">See Prompts</a></blockquote>
    </p>
  </div>

  <div>
    <RSSSources />
  </div>

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
