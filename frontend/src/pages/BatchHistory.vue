<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const sourceLabel = { window: '窗内', request: '覆盖值', default: '默认' }
const parse = (t) => { try { return JSON.parse(t) } catch { return {} } }
const dash = (v) => (v === null || v === undefined || v === '' ? '—' : v)
onMounted(async () => {
  const rows = (await getJSON('/api/history')).items
  items.value = rows.map(h => ({ ...h, input: parse(h.input_json), result: parse(h.result_json) }))
})
</script>
<template><div class="page"><h1>估算记录</h1><table>
<tr><th>#</th><th>时间</th><th>房间</th><th>施工日</th><th>所用涂布率</th><th>来源</th><th>升数</th></tr>
<tr v-for="h in items" :key="h.id">
  <td>#{{ h.id }}</td>
  <td>{{ h.created_at }}</td>
  <td>{{ dash(h.input.room_id) }}</td>
  <td>{{ dash(h.input.work_date) }}</td>
  <td>{{ dash(h.result.coverage ?? h.input.coverage) }}</td>
  <td>{{ sourceLabel[h.input.coverage_source] ?? '—' }}</td>
  <td>{{ dash(h.result.liters) }}</td>
</tr>
</table>
<p class="muted">升数与所用率为写入时钉选值；事后改窗内率或停用窗口，旧条不随之变化。</p>
</div></template>
