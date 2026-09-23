<script setup>
import { ref } from 'vue'
import { postJSON } from '../api'
const room_id = ref(1)
const work_date = ref('')
const out = ref(null)
const err = ref('')
const run = async () => {
  err.value = ''
  out.value = null
  try {
    const body = { room_id: room_id.value, persist: true }
    if (work_date.value) body.work_date = work_date.value
    out.value = await postJSON('/api/estimate', body)
  } catch (e) { err.value = e.message }
}
const sourceText = (src) => ({ season_window: '季节窗口', request: '请求覆盖值', default: '系统默认' })[src] || src
</script>
<template><div class="page"><h1>估漆工作台</h1>
<label>房间ID <input v-model.number="room_id" /></label>
<label style="margin-left:1rem">施工日 <input type="date" v-model="work_date" /></label>
<button @click="run" style="margin-left:1rem">估算</button>
<p v-if="err" style="color:#c0392b">{{ err }}</p>
<p v-if="out">
  净 {{ out.net_m2 }} m² · {{ out.liters }} 升 · {{ out.coats }} 遍<br />
  判定涂布率：{{ out.coverage }} m²/升（来源：{{ sourceText(out.coverage_source) }}）<template v-if="out.work_date"> · 施工日 {{ out.work_date }}</template>
</p></div></template>
