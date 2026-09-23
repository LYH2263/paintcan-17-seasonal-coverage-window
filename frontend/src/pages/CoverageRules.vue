<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const s = ref({})
const w = ref({ enabled: false, start_month: 6, start_day: 1, end_month: 8, end_day: 31, coverage: 6 })
const msg = ref('')

const load = async () => {
  s.value = await getJSON('/api/settings')
  if (s.value.season_window) w.value = { ...s.value.season_window }
}
const save = async () => {
  msg.value = ''
  try {
    w.value = await putJSON('/api/settings/season-window', w.value)
    msg.value = '已保存'
  } catch (e) {
    msg.value = '保存被拒：' + e.message
  }
}
onMounted(load)
</script>
<template><div class="page">
  <h1>遮盖力参数</h1>
  <p>默认每升可刷 {{ s.coverage }} m² · 默认 {{ s.coats }} 遍</p>
  <h2>季节窗口</h2>
  <p>施工日落入窗口时按窗内涂布率换算升数；窗外走估漆台覆盖值或系统默认。</p>
  <p><label><input type="checkbox" v-model="w.enabled" /> 启用季节窗口</label></p>
  <table>
    <tr>
      <th>起</th><th>止</th><th>窗内涂布率 (m²/升)</th>
    </tr>
    <tr>
      <td>
        <input type="number" min="1" max="12" v-model.number="w.start_month" style="width:4rem" /> 月
        <input type="number" min="1" max="31" v-model.number="w.start_day" style="width:4rem" /> 日
      </td>
      <td>
        <input type="number" min="1" max="12" v-model.number="w.end_month" style="width:4rem" /> 月
        <input type="number" min="1" max="31" v-model.number="w.end_day" style="width:4rem" /> 日
      </td>
      <td><input type="number" min="0" step="0.1" v-model.number="w.coverage" style="width:7rem" /></td>
    </tr>
  </table>
  <p>
    <button @click="save">保存窗口</button>
    <span v-if="msg" style="margin-left:1rem">{{ msg }}</span>
  </p>
  <p v-if="!w.enabled" style="color:#b06a00">窗口已停用：新测一律走请求体覆盖值或系统默认。</p>
</div></template>
