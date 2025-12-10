<template>
  <div class="step">
    <h2>Шаг 1: Загрузка текстовых данных</h2>
    
    <div class="upload-section">
      <div class="upload-options">
        <button @click="showExamples = true" class="example-btn">📋 Показать пример</button>
        <button @click="$emit('clear-all')" class="clear-btn">❌ Очистить все</button>
      </div>

      <!-- Модальное окно выбора примера -->
      <div v-if="showExamples" class="modal-overlay">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Выберите пример данных</h3>
            <button @click="showExamples = false" class="close-modal">×</button>
          </div>
          <div class="examples-grid">
            <div 
              v-for="example in availableExamples" 
              :key="example.id"
              class="example-card"
              @click="loadExample(example.id)"
            >
              <h4>{{ example.name }}</h4>
              <p>Документов: {{ example.count }}</p>
              <button class="select-example-btn">Выбрать</button>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="showExamples = false" class="cancel-btn">Отмена</button>
          </div>
        </div>
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
import { ref, computed, onMounted } from 'vue'
import { useExamplesStore } from '@/stores/examples'

const examplesStore = useExamplesStore()

const showExamples = ref(false)
const availableExamples = ref([])

const props = defineProps({
  documents: {
    type: Array,
    required: true
  },
  canAnalyze: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits([
  'add-document',
  'remove-document',
  'clear-all',
  'load-example',
  'analyze-documents'
])


onMounted(() => {
  availableExamples.value = examplesStore.getAvailableExamples()
})


const loadExample = (exampleId) => {
  const exampleData = examplesStore.getExampleData(exampleId)
  emit('load-example', exampleData)
  showExamples.value = false
}
</script>

<style scoped>
.step {
  margin-bottom: 30px;
  position: relative;
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

/* Стили для модального окна */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 10px;
  padding: 0;
  max-width: 800px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.close-modal {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #7f8c8d;
}

.close-modal:hover {
  color: #e74c3c;
}

.examples-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
  padding: 20px;
}

.example-card {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.example-card:hover {
  border-color: #3498db;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.example-card h4 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.example-card p {
  margin: 0 0 15px 0;
  color: #7f8c8d;
  font-size: 14px;
}

.select-example-btn {
  background: #27ae60;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
}

.select-example-btn:hover {
  background: #219a52;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #eee;
  text-align: right;
}

.cancel-btn {
  background: #95a5a6;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
}

.cancel-btn:hover {
  background: #7f8c8d;
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
  
  .examples-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    margin: 10px;
  }
}
</style>