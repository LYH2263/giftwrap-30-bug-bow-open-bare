<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const s = ref({})
const err = ref('')

onMounted(async () => {
  try {
    s.value = await getJSON('/api/settings')
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>

<template>
  <div class="page">
    <h1>设置</h1>
    <p class="lede">当前全局参数只读展示；折边系数请走「折边系数」页，默认结长请走「丝带」页对照修改。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <ul v-else class="item-list">
      <li>
        <span>折边系数 overlap</span>
        <span class="meta">{{ s.overlap }}</span>
      </li>
      <li>
        <span>默认结长 bow_m（米）</span>
        <span class="meta">{{ s.bow_m ?? '—' }}</span>
      </li>
    </ul>
  </div>
</template>
