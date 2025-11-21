<template>
  <div class="error-message">
    {{ error }}
    <button @click="$emit('clear-error')" class="close-error">×</button>
  </div>
</template>

<script setup>
defineProps({
  error: {
    type: String,
    required: true
  }
})

defineEmits(['clear-error'])
</script>

<style scoped>
.error-message {
  background: #e74c3c;
  color: white;
  padding: 15px;
  border-radius: 5px;
  margin: 20px 0;
  position: relative;
}

.close-error {
  position: absolute;
  right: 10px;
  top: 10px;
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
}
</style>