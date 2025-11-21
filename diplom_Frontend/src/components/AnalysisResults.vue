<template>
  <div class="step">
    <h2>Шаг 2: Результаты анализа</h2>
    <p>Обнаружено тем: {{ topics.length }}</p>
    
    <div class="theme-selection">
      <h3>Выберите тему для детального анализа:</h3>
      <div class="themes-grid">
        <div 
          v-for="topic in topics" 
          :key="topic.topic_name"
          class="theme-card"
          :class="{ selected: selectedTopic === topic.topic_name }"
          @click="$emit('select-topic', topic.topic_name)"
        >
          <h4>{{ topic.topic_name }}</h4>
          <p>Документов: {{ topic.document_count }}</p>
          <p>Ключевые слова: {{ topic.keywords.slice(0, 3).join(', ') }}...</p>
        </div>
      </div>
      
      <button 
        @click="$emit('next-step')" 
        class="next-btn" 
        :disabled="!selectedTopic"
      >
        Выбрать временной диапазон
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  topics: {
    type: Array,
    required: true
  },
  selectedTopic: {
    type: String,
    default: ''
  }
})

defineEmits(['select-topic', 'next-step'])
</script>

<style scoped>
.step {
  margin-bottom: 30px;
}

h2 {
  color: #34495e;
  margin-bottom: 20px;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
}

h3 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.themes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
  margin: 20px 0;
}

.theme-card {
  background: #ecf0f1;
  padding: 15px;
  border-radius: 8px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s;
}

.theme-card:hover {
  border-color: #3498db;
}

.theme-card.selected {
  border-color: #e74c3c;
  background: #ffeaa7;
}

.theme-card h4 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.next-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 12px 25px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  width: 100%;
}

.next-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .themes-grid {
    grid-template-columns: 1fr;
  }
}
</style>