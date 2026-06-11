<template>
  <v-text-field
    v-model="schoolNumber"
    label="លេខសាលា / School Number"
    placeholder="បញ្ចូលលេខសាលា..."
    prepend-inner-icon="mdi-school"
    variant="outlined"
    clearable
    persistent-hint
    :hint="isPlaying ? 'កំពុងលេងសំឡេង...' : 'ចុចរូបខាងក្រោមដើម្បីស្តាប់ម្តងទៀត'"
    @focus="handleFocus"
  >
    <template v-slot:append-inner>
      <v-btn
        icon
        size="small"
        variant="text"
        :loading="isPlaying"
        :disabled="isPlaying"
        @click="playHint"
      >
        <v-icon>mdi-volume-high</v-icon>
      </v-btn>
    </template>
  </v-text-field>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const schoolNumber = ref('')
const isPlaying      = ref(false)
const hasAutoPlayed  = ref(false)   // ← key flag to prevent repeat auto-play

let audio = null

const AUDIO_URL = '/sound/123.mp3'   // adjust if needed

function initAudio() {
  if (audio) return

  audio = new Audio(AUDIO_URL)

  audio.oncanplaythrough = () => {
    console.log('Audio ready to play')
  }

  audio.onended = () => {
    isPlaying.value = false
    console.log('Audio finished')
  }

  audio.onerror = (e) => {
    console.error('Audio error:', e)
    isPlaying.value = false
  }
}

function playHint() {
  initAudio()
  if (!audio) return

  // Stop if already playing
  if (isPlaying.value) {
    audio.pause()
    audio.currentTime = 0
    isPlaying.value = false
    return
  }

  // Play
  audio.currentTime = 0
  isPlaying.value = true

  audio.play()
    .then(() => console.log('Playing started'))
    .catch(err => {
      console.warn('Play failed:', err.message)
      isPlaying.value = false
    })
}

function handleFocus() {
  // Auto-play only the VERY FIRST time the field gets focus
  if (!hasAutoPlayed.value && !isPlaying.value) {
    hasAutoPlayed.value = true
    playHint()
  }
  // After first time → do nothing on focus (user uses button instead)
}

onMounted(() => {
  initAudio()           // preload
})

onUnmounted(() => {
  if (audio) {
    audio.pause()
    audio.src = ''
    audio = null
  }
})
</script>

<style scoped>
/* Optional: subtle highlight when focused */
.v-field--focused {
  transition: all 0.2s;
}
</style>