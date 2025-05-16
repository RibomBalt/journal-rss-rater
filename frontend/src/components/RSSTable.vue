<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import Datepicker from '@vuepic/vue-datepicker';
import StarRate from './StarRate.vue'
import '@vuepic/vue-datepicker/dist/main.css';
// import { useRoute } from 'vue-router'
import axios from 'axios'

// let route = useRoute();

// TODO: use dotenv or something to set the base URL
const BASE_URL = window.location.pathname.replace(/\/+$/, '');
const RSS_API = `${BASE_URL}/api/rss`;

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
const data_views = ref<RSSView[]>([]);
const current_sort_field = ref<string>('llm_score');
const current_sort_ascending = ref<boolean>(false);

// filters
const max_number = ref(1000);
const date_selected = ref([Date.now() - 1000 * 60 * 60 * 24 * 7, Date.now()]); // default to one week ago

// filters without ajax
const key_words = ref<string>("");

// filter by keywords & journals
const data_views_filtered = computed(() => {
  return data_views.value.filter(item => {
    const keywords = key_words.value.split(' ').map(k => k.toLowerCase());
    const target = `${item.data.title} ${item.data.summary} ${item.data.source} ${item.data.llm_comments}`;
    return keywords.every(keyword => target.toLowerCase().includes(keyword));
  }).filter(item => {
    return selected_journals.value.some(journal => {
      return journal.show && item.data.source === journal.source;
    });
  });
});

interface RSSSource {
  source: string;
  feed: string;
  show: boolean;

  [index: string]: any; // allow for other fields
}
const selected_journals = ref<RSSSource[]>([]);

// AJAX
async function fetchRSSItems(max_number: Number, timestamp_range: number[]) {
  const date_range_str = timestamp_range.map(t => {
    const date = new Date(t);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
  });

  try {
    const response = await axios.request<RSSDataView[]>({
      url: RSS_API,
      method: 'get',
      params: {
        max_number: max_number,
        time_since: date_range_str[0],
        time_until: date_range_str[1],
      }
    })
    // const old_link_list = data_views.value.map(item => item.data.link);

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

async function fetchRSSSources() {
  try {
    const response = await axios.get<RSSSource[]>(`${RSS_API}/sources`);
    selected_journals.value = response.data.map(item => {
      return {
        ...item,
        show: true
      }
    });
  } catch (error) {
    console.error('Error fetching RSS sources:', error);
  }
}

// sort/toggle on table
function toggleSummaryShrink(item: RSSView) {
  item.style.shrink_summary = !item.style.shrink_summary;
}
function toggleCommentShrink(item: RSSView) {
  item.style.shrink_comment = !item.style.shrink_comment;
}
function toggleJournalShow(journal: RSSSource) {
  journal.show = !journal.show;
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

// mount/watch
onMounted(async () => {
  await fetchRSSSources();
  await fetchRSSItems(max_number.value, date_selected.value);
})

watch([
  () => max_number.value,
  () => date_selected.value
], async () => {
  await fetchRSSItems(max_number.value, date_selected.value);
})

</script>


<template>
  <div class="rss-filter-root">
    <h3>Filter</h3>
    <div class="rss-filter-form">
      <div>
        <label for="max_number">Max number of items:</label>
        <input type="number" id="max_number" v-model.number="max_number" />
      </div>

      <div>
        <label for="date_selected">Date from:</label>
        <div>
          <Datepicker v-model="date_selected" range position="left" />
        </div>
      </div>
      <div>
        <label for="key_words">Keywords</label>
        <input type="text" id="key_words" v-model="key_words" />
      </div>

      <div v-if="selected_journals.length > 0" class="rss-source-item-box">
        <label>Journals</label>
        <div v-for="journal in selected_journals" :key="journal.source" :class="{'rss-source-item': true, 'rss-source-item-box-activate': journal.show }" @click="toggleJournalShow(journal)">
          <p>{{ journal.source }}</p>
        </div>
      </div>

    </div>
  </div>

  <div>
    <hr />
  </div>

  <div class="rss-table-root">
    <table>
      <thead>
        <tr>
          <th v-for="column in table_columns" :key="column.field"
            @click="sort_by_field(column.field, (!current_sort_ascending))">
            {{ column.name }}{{ current_sort_field === column.field ? (current_sort_ascending ? '⬆️' : '⬇️') : '' }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in data_views_filtered" :key="item.data.link">
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
          <td>
            <StarRate v-model.number="item.data.llm_score" />
          </td>
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

.rss-filter-form {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* TODO: datepicker width too short */
.rss-filter-form>div {
  display: flex;
  flex-direction: row;
  align-items: baseline;
}

.rss-filter-form label {
  font-weight: bold;
  margin-right: 10px;
}

.rss-source-item {
  margin: 10px 0;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 10px;
}

.rss-source-item-box {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  align-items: left;
}

.rss-source-item-box-activate {
  background-color:rgb(194, 94, 132);
}

th,
td {
  border: 1px solid #ccc;
}

th {
  background-color: #518b9c;
}

td {
  background-color: #1a2b30;
}
</style>