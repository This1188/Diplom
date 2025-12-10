<template>
  <div class="step">
    <h2>Шаг 3: Выбор временного диапазона</h2>
    <p>Выбранная тема: <strong>{{ selectedTopic }}</strong></p>
    <p>Документов в теме: <strong>{{ topicDocuments.length }}</strong></p>
    
    <div class="date-range-section">
      <div class="selection-methods">
        <div class="method-tabs">
          <button 
            @click="activeMethod = 'chart'" 
            class="tab-btn"
            :class="{ active: activeMethod === 'chart' }"
          >
            📊 Выбор на графике
          </button>
          <button 
            @click="activeMethod = 'manual'" 
            class="tab-btn"
            :class="{ active: activeMethod === 'manual' }"
          >
            📅 Ручной ввод
          </button>
        </div>

        <!-- Выбор на графике -->
        <div v-if="activeMethod === 'chart'" class="chart-method">
          <div v-if="topicDocuments.length > 0">
            <DateRangeChart 
              :documents="topicDocuments"
              @range-selected="handleChartRangeSelection"
            />
          </div>
          <div v-else class="no-documents">
            <p>Нет документов в выбранной теме</p>
          </div>
        </div>

        <!-- Ручной ввод -->
        <div v-if="activeMethod === 'manual'" class="manual-method">
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
            <button @click="setDateRange('lastWeek')" class="suggestion-btn">За последнюю неделю</button>
            <button @click="setDateRange('lastMonth')" class="suggestion-btn">За последний месяц</button>
            <button @click="setDateRange('all')" class="suggestion-btn">Весь период</button>
          </div>
        </div>

        <div class="current-selection">
          <h4>Текущий выбор:</h4>
          <div class="selection-info">
            <p><strong>Начало:</strong> {{ dateRange.start || 'не выбрано' }}</p>
            <p><strong>Конец:</strong> {{ dateRange.end || 'не выбрано' }}</p>
            <p><strong>Документов в периоде:</strong> {{ documentsInRange.length }}</p>
          </div>
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
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import DateRangeChart from './DateRangeChart.vue'

const props = defineProps({
  selectedTopic: {
    type: String,
    required: true
  },
  documents: {
    type: Array,
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
  canGenerateSummary: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['set-date-range', 'generate-summary'])

const activeMethod = ref('chart')


const selectedTopicInfo = computed(() => {
  return props.topics.find(topic => topic.topic_name === props.selectedTopic)
})


const topicDocuments = computed(() => {
  if (!selectedTopicInfo.value) return []
  
  const selectedTopicObj = props.topics.find(t => t.topic_name === props.selectedTopic)
  if (!selectedTopicObj || !selectedTopicObj.document_indices) return []
  
  return selectedTopicObj.document_indices.map(index => props.documents[index])
})


const documentsInRange = computed(() => {
  if (!props.dateRange.start || !props.dateRange.end) return []
  
  return topicDocuments.value.filter(doc => {
    const docDate = new Date(doc.date)
    const startDate = new Date(props.dateRange.start)
    const endDate = new Date(props.dateRange.end)
    return docDate >= startDate && docDate <= endDate
  })
})

const handleChartRangeSelection = (range) => {
  props.dateRange.start = range.start
  props.dateRange.end = range.end
}


const setDateRange = (range) => {
  const today = new Date()
  
  if (topicDocuments.value.length === 0) return
  
  const docDates = topicDocuments.value.map(doc => new Date(doc.date))
  
  switch (range) {
    case 'lastWeek':
      const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
      props.dateRange.start = lastWeek.toISOString().split('T')[0]
      props.dateRange.end = today.toISOString().split('T')[0]
      break
    case 'lastMonth':
      const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate())
      props.dateRange.start = lastMonth.toISOString().split('T')[0]
      props.dateRange.end = today.toISOString().split('T')[0]
      break
    case 'all':
      if (topicDocuments.value.length > 0) {
        const minDate = new Date(Math.min(...docDates)).toISOString().split('T')[0]
        const maxDate = new Date(Math.max(...docDates)).toISOString().split('T')[0]
        props.dateRange.start = minDate
        props.dateRange.end = maxDate
      }
      break
  }
}


watch(() => [props.selectedTopic, topicDocuments.value], ([newTopic, newDocs]) => {
  if (newTopic && newDocs.length > 0 && (!props.dateRange.start || !props.dateRange.end)) {
    setDateRange('all')
  }
}, { immediate: true })
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

.selection-methods {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.method-tabs {
  display: flex;
  gap: 10px;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 15px;
}

.tab-btn {
  background: #95a5a6;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 5px 5px 0 0;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.tab-btn.active {
  background: #3498db;
  transform: translateY(-2px);
}

.tab-btn:hover:not(.active) {
  background: #7f8c8d;
}

.chart-method, .manual-method {
  background: white;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.manual-method {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.date-inputs {
  display: flex;
  gap: 20px;
  justify-content: center;
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

.current-selection {
  background: white;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.current-selection h4 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 10px;
}

.selection-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.selection-info p {
  margin: 0;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 14px;
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
  margin-top: 10px;
}

.generate-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.generate-btn:not(:disabled):hover {
  background: #d35400;
}

@media (max-width: 768px) {
  .date-inputs {
    flex-direction: column;
    align-items: center;
  }
  
  .date-suggestions {
    flex-direction: column;
  }
  
  .method-tabs {
    flex-direction: column;
  }
  
  .selection-info {
    grid-template-columns: 1fr;
  }
}
</style>