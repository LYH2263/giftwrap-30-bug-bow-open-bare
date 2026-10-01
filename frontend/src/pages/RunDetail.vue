<script setup>
// 详情只认落库快照：bow_enabled / bow_m / ribbon_m 均按写入值展示

import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const props = defineProps({ id: String })
const run = ref(null)
const err = ref('')

onMounted(async () => {
  try {
    run.value = await getJSON(`/api/runs/${props.id}`)
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>

<template>
  <div class="page">
    <p v-if="err" class="bad">{{ err }}</p>
    <template v-else-if="run">
      <h1>用纸档 #{{ run.id }}</h1>
      <p class="lede">
        {{ run.box_name }} · 折边系数 {{ run.overlap }} ·
        <span class="pill" :class="{ warn: !run.result?.bow_enabled }">
          {{ run.result?.bow_enabled ? `蝴蝶结 结长 ${run.result.bow_m} m` : '未打蝴蝶结' }}
        </span>
      </p>

      <div class="metric-grid">
        <div class="metric-tile paper">
          <span class="metric-label">用纸面积（落库）</span>
          <span class="metric-value">{{ run.result?.paper_m2 ?? '—' }}<i>m²</i></span>
          <span class="metric-sub">钉住写入值，不随后续设置变化</span>
        </div>
        <div class="metric-tile ribbon-tile">
          <span class="metric-label">丝带总长（落库）</span>
          <span class="metric-value">{{ run.result?.ribbon_m ?? '—' }}<i>m</i></span>
          <span class="metric-sub">
            捆扎 {{ run.result?.ribbon?.base_ribbon_m ?? '—' }} m
            <template v-if="run.result?.bow_enabled">＋ 结长 {{ run.result.bow_m }} m</template>
          </span>
        </div>
      </div>

      <ul class="item-list detail-list">
        <li><span>bow_enabled</span><span class="meta">{{ String(run.result?.bow_enabled) }}</span></li>
        <li><span>bow_m（结长）</span><span class="meta">{{ run.result?.bow_m }} m</span></li>
        <li><span>ribbon_m（丝带）</span><span class="meta">{{ run.result?.ribbon_m }} m</span></li>
        <li><span>paper_m2（纸面积）</span><span class="meta">{{ run.result?.paper_m2 }} m²</span></li>
        <li><span>wrap_style</span><span class="meta">{{ run.result?.ribbon?.wrap_style }}</span></li>
        <li><span>写入时间</span><span class="meta">{{ run.created_at }}</span></li>
      </ul>

      <div class="row" style="margin-top: 1.25rem">
        <router-link class="btn" to="/history">返回用纸档</router-link>
        <router-link class="btn ghost" to="/bench">去算纸台同参再算</router-link>
        <router-link class="btn ghost" to="/ribbon">去丝带页</router-link>
      </div>
    </template>
  </div>
</template>
