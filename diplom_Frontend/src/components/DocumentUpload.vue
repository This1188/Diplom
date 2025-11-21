<template>
  <div class="step">
    <h2>Шаг 1: Загрузка текстовых данных</h2>
    
    <div class="upload-section">
      <div class="upload-options">
        <button @click="$emit('load-example')" class="example-btn">📋 Показать пример</button>
        <button @click="$emit('clear-all')" class="clear-btn">❌ Очистить все</button>
      </div>

      <div v-for="(document, index) in documents" :key="index" class="document-row">
        <input 
          type="date" 
          v-model="document.date"
          class="date-input"
        >
        <input 
          type="text" 
          v-model="document.theme"
          placeholder="Тема"
          class="theme-input"
        >
        <textarea 
          v-model="document.text"
          placeholder="Текст документа"
          class="text-input"
          rows="3"
        ></textarea>
        <button 
          @click="$emit('remove-document', index)"
          class="remove-btn"
          v-if="documents.length > 1"
        >×</button>
      </div>
      
      <button @click="$emit('add-document')" class="add-btn">+ Добавить документ</button>
      
      <div class="documents-count">
        Всего документов: {{ documents.length }}
      </div>
      
      <button 
        @click="$emit('analyze-documents')" 
        class="analyze-btn" 
        :disabled="!canAnalyze"
      >
        Анализировать документы
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  documents: {
    type: Array,
    required: true
  },
  canAnalyze: {
    type: Boolean,
    required: true
  }
})

defineEmits([
  'add-document',
  'remove-document',
  'clear-all',
  'load-example',
  'analyze-documents'
])
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

.upload-options {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.example-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
}

.clear-btn {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
}

.document-row {
  display: grid;
  grid-template-columns: 150px 200px 1fr auto;
  gap: 10px;
  margin-bottom: 15px;
  align-items: start;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 5px;
}

.date-input, .theme-input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.text-input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
  font-family: inherit;
}

.remove-btn {
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  font-size: 16px;
}

.add-btn {
  background: #27ae60;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
  margin-right: 10px;
}

.analyze-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 12px 25px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 20px;
  width: 100%;
}

.analyze-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.documents-count {
  text-align: center;
  margin: 15px 0;
  font-weight: bold;
  color: #7f8c8d;
}

@media (max-width: 768px) {
  .document-row {
    grid-template-columns: 1fr;
  }
}
</style>