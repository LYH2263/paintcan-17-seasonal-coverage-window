<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const sourceText = (src) => ({ season_window: '季节窗口', request: '请求覆盖值', default: '系统默认' })[src] || (src || '—')
// 写入时所用率与升数冻结在 input_json/result_json 中，改窗口或停用窗口不影响旧条
const rows = () => items.value.map(h => {
  let inp = {}, res = {}
  try { inp = JSON.parse(h.input_json || '{}') } catch { }
  try { res = JSON.parse(h.result_json || '{}') } catch { }
  return { ...h, inp, res }
})
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
</script>
<template><div class="page"><h1>估算记录</h1>
<table>
  <tr><th>#</th><th>时间</th><th>施工日</th><th>所用涂布率 (m²/升)</th><th>来源</th><th>升数</th></tr>
  <tr v-for="h in rows()" :key="h.id">
    <td>#{{ h.id }}</td>
    <td>{{ h.created_at }}</td>
    <td>{{ h.inp.work_date || '—' }}</td>
    <td>{{ h.inp.coverage ?? h.res.coverage ?? '—' }}</td>
    <td>{{ sourceText(h.inp.coverage_source) }}</td>
    <td>{{ h.res.liters ?? '—' }}</td>
  </tr>
</table>
</div></template>
