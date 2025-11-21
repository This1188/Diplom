<template>
  <div class="step">
    <h2>Шаг 3: Выбор временного диапазона</h2>
    <p>Выбранная тема: <strong>{{ selectedTopic }}</strong></p>
    
    <div class="date-range-section">
      <div class="date-inputs">
        <label>
          Начальная дата:
          <input type="date" v-model="dateRange.start" class="date-input">
        </label>
        <label>
          Конечная дата:
          <input type="date" v-model="dateRange.end" class="date-input">
        </label>
      </div>
      
      <div class="date-suggestions">
        <button @click="$emit('set-date-range', 'lastWeek')" class="suggestion-btn">За последнюю неделю</button>
        <button @click="$emit('set-date-range', 'lastMonth')" class="suggestion-btn">За последний месяц</button>
        <button @click="$emit('set-date-range', 'all')" class="suggestion-btn">Весь период</button>
      </div>
      
      <button 
        @click="$emit('generate-summary')" 
        class="generate-btn" 
        :disabled="!canGenerateSummary"
      >
        Сформировать справку
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  selectedTopic: {
    type: String,
    required: true
  },
  documents: {
    type: Array,
    required: true
  },
  dateRange: {
    type: Object,
    required: true
  },
  canGenerateSummary: {
    type: Boolean,
    required: true
  }
})

defineEmits(['set-date-range', 'generate-summary'])
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

.date-range-section {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.date-inputs {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.date-inputs label {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-weight: bold;
}

.date-suggestions {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.suggestion-btn {
  background: #95a5a6;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
}

.suggestion-btn:hover {
  background: #7f8c8d;
}

.generate-btn {
  background: #e67e22;
  color: white;
  border: none;
  padding: 12px 25px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  width: 100%;
}

.generate-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .date-inputs {
    flex-direction: column;
    align-items: center;
  }
  
  .date-suggestions {
    flex-direction: column;
  }
}
</style>