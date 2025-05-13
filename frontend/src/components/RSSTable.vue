<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import Datepicker from '@vuepic/vue-datepicker';
import StarRate from './StarRate.vue'
import '@vuepic/vue-datepicker/dist/main.css';
import { useRoute } from 'vue-router'
// import RSSItem from '../datamodels/RSSItem'
import axios from 'axios'

let route = useRoute();

let max_number = computed(() => {
    return (route && route.query.max_number) ? parseInt(route.query.max_number as string) : 100;
});
// const max_number = (route && route.query.max_number) ? parseInt(route.query.max_number as string) : 100;
// const max_number = 100; // default value

const date_selected = ref();

const BASE_URL = ""
const RSS_API = `${BASE_URL}/api/rss?max_number=${max_number.value}`;

interface RSSStyle {
    shrink_summary: boolean;
    shrink_comment: boolean;
}

interface RSSDataView {
    title: string;
    link: string;
    summary: string;
    published: Date;
    source: string;
    llm_comments: string | null;
    llm_score: number | null;

    [index: string]: any; // allow for other fields
}

interface RSSView {
    data: RSSDataView;
    style: RSSStyle;
}

interface Column {
    name: string;
    field: string;
}

const table_columns: Column[] = [
    { name: 'Title', field: 'title' },
    { name: 'Source', field: 'source' },
    { name: 'Summary', field: 'summary' },
    { name: 'Published', field: 'published' },
    { name: 'LLM Comments', field: 'llm_comments' },
    { name: 'LLM Score', field: 'llm_score' }
];

// hardcode the fields on RSSItem
let data_views = ref<RSSView[]>([]);
let current_sort_field = ref<string>('llm_score');
let current_sort_ascending = ref<boolean>(false);

async function fetchRSSItems() {
    try {
        const response = await axios.get<RSSDataView[]>(RSS_API)
        data_views.value = response.data.map(item => {
            return {
                data: item,
                style: {
                    shrink_summary: item.summary.length > 50,
                    shrink_comment: (item.llm_comments !== null) && (item.llm_comments.length > 30)
                }
            };
        });
        sort_by_field(current_sort_field.value, current_sort_ascending.value);

    } catch (error) {
        console.error('Error fetching RSS items:', error)
    }
}

function toggleSummaryShrink(item: RSSView) {
    item.style.shrink_summary = !item.style.shrink_summary;
}
function toggleCommentShrink(item: RSSView) {
    item.style.shrink_comment = !item.style.shrink_comment;
}
function sort_by_field(field: string, ascending: boolean = true) {
    data_views.value.sort((a, b) => {
        const ascendingModifier = ascending ? 1 : -1;
        if (a.data[field] < b.data[field]) return -ascendingModifier;
        if (a.data[field] > b.data[field]) return ascendingModifier;
        return 0;
    });
    current_sort_ascending.value = ascending;
    current_sort_field.value = field;
}

onMounted(async () => {
    await fetchRSSItems();
})

// watch(max_number)

</script>


<template>
  <div>
    <Datepicker v-model="date_selected" />
  </div>

  <div>
    <table>
      <thead>
        <tr>
          <th v-for="column in table_columns" :key="column.field" @click="sort_by_field(column.field, (!current_sort_ascending))">
            {{ column.name }} {{ current_sort_field === column.field ? (current_sort_ascending ? '⬆️' : '⬇️') : '' }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in data_views" :key="item.data.link">
          <td><a :href="item.data.link" target="_blank">{{ item.data.title }}</a></td>
          <td>{{ item.data.source }}</td>
          <td>
            <div :class="{ 'shrink-height': item.style.shrink_summary }" @click="toggleSummaryShrink(item)">{{
              item.data.summary }}</div>
          </td>
          <td>{{ item.data.published }}</td>
          <td>
            <div :class="{ 'shrink-height': item.style.shrink_comment }" @click="toggleCommentShrink(item)">{{
              item.data.llm_comments }}</div>
          </td>
          <td><StarRate v-model.number="item.data.llm_score" /></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
a {
  color: rgb(190, 190, 103);
}
.shrink-height {
    max-height: 50px;
    overflow-y: clip;
    background-color: #666;
}

th, td {
  border: 1px solid #ccc;
}

th {
  background-color: #518b9c;
}
td {
  background-color: #1a2b30;
}
</style>