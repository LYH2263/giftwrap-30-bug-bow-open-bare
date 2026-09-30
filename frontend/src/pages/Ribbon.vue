<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'

const boxes = ref([])
const bid = ref(1)
const wrapStyle = ref('cross')
const bowEnabled = ref(true)
const defaultBowM = ref(0.3)
const bowM = ref(0.3)
const out = ref(null)
const runs = ref([])
const err = ref('')
const savedMsg = ref('')
const busy = ref(false)

async function loadRuns() {
  runs.value = (await getJSON('/api/runs?limit=8')).items
}

onMounted(async () => {
  try {
    boxes.value = (await getJSON('/api/boxes')).items.filter((b) => b.data_quality === 'clean')
    if (boxes.value.length) bid.value = boxes.value[0].id
    const s = await getJSON('/api/settings')
    defaultBowM.value = Number(s.bow_m ?? 0.3)
    bowM.value = defaultBowM.value
    await loadRuns()
  } catch (e) {
    err.value = String(e.message || e)
  }
})

function qs() {
  return new URLSearchParams({
    box_id: String(bid.value),
    wrap_style: wrapStyle.value,
    bow_enabled: String(bowEnabled.value),
    bow_m: String(bowM.value ?? defaultBowM.value),
  })
}

async function dryRun() {
  err.value = ''
  busy.value = true
  try {
    out.value = await getJSON(`/api/estimate?${qs()}`)
  } catch (e) {
    out.value = null
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}

async function saveDefault() {
  err.value = ''
  savedMsg.value = ''
  if (!(Number(bowM.value) > 0)) {
    err.value = '默认结长必须大于 0'
    return
  }
  try {
    const s = await postJSON('/api/settings/bow_m', { bow_m: Number(bowM.value) })
    defaultBowM.value = Number(s.bow_m)
    savedMsg.value = `默认结长已改为 ${s.bow_m} m；历史用纸档仍以落库为准，不会重算。`
  } catch (e) {
    err.value = String(e.message || e)
  }
}
</script>

<template>
  <div class="page">
    <h1>丝带</h1>
    <p class="lede">
      捆扎长度跟盒体三边走；打蝴蝶结时总长 = 捆扎米数 + 结长。结长只加丝带，纸面积纹丝不动。
    </p>

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
      <button :disabled="busy" @click="dryRun">干算丝带</button>
      <button class="ghost" :disabled="!bowEnabled" @click="saveDefault">存为默认结长</button>
    </div>
    <p class="stat-line">当前默认结长：{{ defaultBowM }} m（只影响以后的新算，历史用纸档钉住写入值）。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <p v-if="savedMsg" class="ok-note">{{ savedMsg }}</p>

    <div v-if="out" class="result-board">
      <div class="metric-grid">
        <div class="metric-tile paper">
          <span class="metric-label">用纸面积</span>
          <span class="metric-value">{{ out.paper_m2 }}<i>m²</i></span>
          <span class="metric-sub">与算纸台同参一致，不随结长变</span>
        </div>
        <div class="metric-tile ribbon-tile">
          <span class="metric-label">丝带总长</span>
          <span class="metric-value">{{ out.ribbon.ribbon_m }}<i>m</i></span>
          <span class="metric-sub">
            捆扎 {{ out.ribbon.base_ribbon_m }} m
            <template v-if="out.ribbon.bow_enabled">＋ 结长 {{ out.ribbon.bow_m }} m</template>
            <template v-else>（未打结）</template>
          </span>
        </div>
      </div>
      <p class="stat-line">
        同参到
        <router-link
          :to="`/bench?box_id=${bid.value}&wrap_style=${wrapStyle}&bow_enabled=${bowEnabled ? 1 : 0}&bow_m=${bowM ?? defaultBowM}`"
        >算纸台</router-link>
        再干算，数值须与此处互证。
      </p>
    </div>

    <h2 class="subhead">最近用纸档（落库摘要）</h2>
    <p v-if="!runs.length" class="empty">还没有写入过。</p>
    <ul v-else class="item-list">
      <li v-for="r in runs" :key="r.id">
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
