<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON, postJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const route = useRoute()
const boxes = ref([])
const bid = ref(1)
const wrapStyle = ref('cross')
const bowEnabled = ref(false)
const bowM = ref(0.3)
const out = ref(null)
const err = ref('')
const busy = ref(false)

onMounted(async () => {
  try {
    boxes.value = (await getJSON('/api/boxes')).items.filter((b) => b.data_quality === 'clean')
    const s = await getJSON('/api/settings')
    bowM.value = Number(s.bow_m ?? 0.3)
    // 接受丝带页“同参”跳转带来的查询参数
    const q = route.query
    if (q.box_id) bid.value = Number(q.box_id)
    else if (boxes.value.length) bid.value = boxes.value[0].id
    if (q.wrap_style) wrapStyle.value = String(q.wrap_style)
    if (q.bow_enabled !== undefined) bowEnabled.value = ['1', 'true'].includes(String(q.bow_enabled))
    if (q.bow_m !== undefined) bowM.value = Number(q.bow_m)
  } catch (e) {
    err.value = String(e.message || e)
  }
})

function params() {
  return {
    box_id: bid.value,
    wrap_style: wrapStyle.value,
    bow_enabled: bowEnabled.value,
    bow_m: bowM.value,
  }
}

async function go(save) {
  err.value = ''
  busy.value = true
  try {
    out.value = save
      ? await postJSON('/api/estimate', { ...params(), save: true })
      : await getJSON(`/api/estimate?${new URLSearchParams({
          box_id: String(bid.value),
          wrap_style: wrapStyle.value,
          bow_enabled: String(bowEnabled.value),
          bow_m: String(bowM.value),
        })}`)
  } catch (e) {
    out.value = null
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>算纸</h1>
    <p class="lede">先试算看面积与丝带，并排对照；确认后再写入用纸档。结长只加丝带，不改纸面积。</p>
    <div class="row">
      <select v-model.number="bid">
        <option v-for="b in boxes" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <select v-model="wrapStyle">
        <option value="cross">十字捆扎</option>
        <option value="band">单道捆扎</option>
      </select>
      <label class="field-check">
        <input v-model="bowEnabled" type="checkbox" />
        打蝴蝶结
      </label>
      <label class="field-num" :class="{ disabled: !bowEnabled }">
        结长
        <input v-model.number="bowM" type="number" min="0.01" step="0.05" :disabled="!bowEnabled" />
        m
      </label>
    </div>
    <div class="row">
      <button :disabled="busy" @click="go(false)">试算</button>
      <button class="ribbon" :disabled="busy" @click="go(true)">写入用纸档</button>
    </div>
    <p v-if="err" class="bad">{{ err }}</p>
    <div v-if="out" class="result-board">
      <div class="metric-grid">
        <div class="metric-tile paper">
          <span class="metric-label">用纸面积</span>
          <span class="metric-value">{{ out.paper_m2 }}<i>m²</i></span>
          <span class="metric-sub">不随结长变化</span>
        </div>
        <div class="metric-tile ribbon-tile">
          <span class="metric-label">丝带总长</span>
          <span class="metric-value">{{ out.ribbon.ribbon_m }}<i>m</i></span>
          <span class="metric-sub">
            捆扎 {{ out.ribbon.base_ribbon_m }} m
            <template v-if="out.ribbon.bow_enabled">＋ 结长 {{ out.ribbon.bow_m }} m</template>
          </span>
        </div>
      </div>
      <p v-if="out.run_id" class="stat-line">
        已写入用纸档 #{{ out.run_id }}，
        <router-link :to="`/history/${out.run_id}`">查看落库详情</router-link>
      </p>
      <BoxUnfold
        :l="out.box.length"
        :w="out.box.width"
        :h="out.box.height"
        :paper-m2="out.paper_m2"
      />
    </div>
  </div>
</template>
