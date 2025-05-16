<script setup lang="ts">
import RSSTable from './components/RSSTable.vue';
import { ref } from 'vue';
// import RSSSources from './components/RSSSources.vue';

const BASE_URL = window.location.pathname.replace(/\/+$/, '');
const RSS_LLM_PROMPT_API = ref(`${BASE_URL}/api/rss/llm_prompt`);
const RSS_SOURCES_API = ref(`${BASE_URL}/api/rss/sources`);

</script>

<template>
  <div style="text-align: center;">
    <h1>Journal RSS Rater</h1>
    <p>从电子期刊的RSS订阅源获取更新，并借助大语言模型对相关性进行打分。</p>
  </div>

  <div style="display: flex; justify-content: space-evenly; align-items: center baseline;">
    <div><a href="https://github.com/RibomBalt/journal-rss-rater"><img alt="github" src="https://raw.githubusercontent.com/rdimascio/icons/refs/heads/master/icons/github.svg" style="width: 16px; ">开放源代码</a></div>
    <div><a :href="RSS_LLM_PROMPT_API">See Prompts</a></div>
    <div><a :href="RSS_SOURCES_API">See RSS Sources</a></div>
  </div>

  <!-- <div>
    <RSSSources />
  </div> -->

    <p style="text-align: left;">使用说明：
      <ul>
        <li>可以选择最多文章数、日期范围、包含关键词、期刊来源。</li>
        <li>点击表头可以排序。</li>
        <li>点击灰底文字可以查看完整内容。</li>
      </ul>
    </p>
  <hr />
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
