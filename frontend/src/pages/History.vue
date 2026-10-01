<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const items = ref([])
const err = ref('')

onMounted(async () => {
  try {
    items.value = (await getJSON('/api/runs')).items
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>

<template>
  <div class="page">
    <h1>用纸档</h1>
    <p class="hint">列表与详情同钉写入快照（bow_enabled / bow_m / ribbon_m）。</p>
    <p class="lede">
      算纸页「写入用纸档」后的落库快照，按次保留盒名、纸面积与丝带米。
      数字只从库里读，改默认结长不会重算历史。
    </p>
    <p v-if="err" class="bad">{{ err }}</p>
    <p v-else-if="!items.length" class="empty">还没有写入过。先去算纸试一单。</p>
    <ul v-else class="item-list">
      <li v-for="r in items" :key="r.id">
        <router-link :to="`/history/${r.id}`">
          #{{ r.id }} {{ r.box_name }}
          <span class="bow-tag" v-if="r.result?.bow_enabled">蝴蝶结 {{ r.result.bow_m }} m</span>
          <span class="bow-tag off" v-else>无结</span>
        </router-link>
        <span class="meta">
          纸 {{ r.result?.paper_m2 ?? '—' }} m² ·
          丝带 <strong>{{ r.result?.ribbon_m ?? '—' }}</strong> m
        </span>
      </li>
    </ul>
  </div>
</template>
