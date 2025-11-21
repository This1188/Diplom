<template>
  <div class="step">
    <h2>Справка по теме</h2>
    
    <div class="summary-section" v-if="summary">
      <div class="summary-header">
        <h3>Тема: {{ selectedTopic }}</h3>
        <p>Период: {{ summary.summary_period.start_date }} - {{ summary.summary_period.end_date }}</p>
        <p>Всего документов в периоде: {{ summary.summary_period.total_documents }}</p>
      </div>
      
      <div class="summary-details">
        <h4>Статистика по теме:</h4>
        <div class="topic-detail">
          <p><strong>Ключевые слова:</strong> {{ getSelectedTopicKeywords().join(', ') }}</p>
          <p><strong>Документов в теме:</strong> {{ getSelectedTopicDocumentCount() }}</p>
          <p><strong>Уверенность анализа:</strong> {{ (getSelectedTopicConfidence() * 100).toFixed(1) }}%</p>
        </div>
      </div>

      <div class="documents-list">
        <h4>Документы в выбранном периоде:</h4>
        <div v-for="doc in getFilteredDocuments()" :key="doc.id" class="document-item">
          <div class="doc-header">
            <span class="doc-date">{{ doc.date }}</span>
            <span class="doc-theme">{{ doc.theme }}</span>
          </div>
          <p class="doc-text">{{ doc.text.substring(0, 150) }}...</p>
        </div>
      </div>
    </div>
    
    <div class="action-buttons">
      <button @click="$emit('reset-app')" class="reset-btn">Начать новый анализ</button>
      <button @click="$emit('back-to-topics')" class="back-btn">Вернуться к выбору темы</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  summary: {
    type: Object,
    default: null
  },
  selectedTopic: {
    type: String,
    required: true
  },
  topics: {
    type: Array,
    required: true
  },
  dateRange: {
    type: Object,
    required: true
  },
  documents: {
    type: Array,
    required: true
  }
})

defineEmits(['reset-app', 'back-to-topics'])

const getSelectedTopicKeywords = () => {
  const topic = props.topics.find(t => t.topic_name === props.selectedTopic)
  return topic ? topic.keywords : []
}

const getSelectedTopicDocumentCount = () => {
  const topic = props.topics.find(t => t.topic_name === props.selectedTopic)
  return topic ? topic.document_count : 0
}

const getSelectedTopicConfidence = () => {
  const topic = props.topics.find(t => t.topic_name === props.selectedTopic)
  return topic ? topic.average_confidence : 0
}

const getFilteredDocuments = () => {
  if (!props.dateRange.start || !props.dateRange.end) return []
  
  return props.documents.filter(doc => {
    const docDate = new Date(doc.date)
    const startDate = new Date(props.dateRange.start)
    const endDate = new Date(props.dateRange.end)
    return docDate >= startDate && docDate <= endDate
  })
}
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

.summary-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 5px;
  margin-bottom: 20px;
}

.summary-header {
  background: white;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
  border-left: 4px solid #3498db;
}

.summary-details {
  background: white;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
}

.topic-detail {
  background: #ecf0f1;
  padding: 15px;
  border-radius: 5px;
}

.documents-list {
  background: white;
  padding: 15px;
  border-radius: 5px;
}

.document-item {
  background: #f8f9fa;
  padding: 15px;
  margin: 10px 0;
  border-radius: 5px;
  border-left: 4px solid #27ae60;
}

.doc-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-weight: bold;
}

.doc-date {
  color: #3498db;
}

.doc-theme {
  color: #e74c3c;
}

.doc-text {
  color: #7f8c8d;
  line-height: 1.4;
}

.action-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.reset-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 12px 25px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}

.back-btn {
  background: #95a5a6;
  color: white;
  border: none;
  padding: 12px 25px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}

@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
  }
}
</style>