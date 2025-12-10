<template>
  <div id="app">
    <div class="container">
      <h1>Анализатор текстовых данных</h1>
      
      <!-- Шаг 1: Загрузка данных -->
      <DocumentUpload 
        v-if="currentStep === 1"
        :documents="documents"
        :can-analyze="canAnalyze"
        @add-document="addDocument"
        @remove-document="removeDocument"
        @clear-all="clearAll"
        @load-example="loadExample"
        @analyze-documents="analyzeDocuments"
      />


      <AnalysisResults 
        v-if="currentStep === 2"
        :topics="topics"
        :selected-topic="selectedTopic"
        @select-topic="selectTopic"
        @next-step="nextStep"
      />

      <DateRangeSelection 
        v-if="currentStep === 3"
        :selected-topic="selectedTopic"
        :documents="documents"
        :topics="topics" 
        :date-range="dateRange"
        :can-generate-summary="canGenerateSummary"
        @set-date-range="setDateRange"
        @generate-summary="generateSummary"
      />

      <SummaryReport 
        v-if="currentStep === 4"
        :summary="summary"
        :selected-topic="selectedTopic"
        :topics="topics"
        :date-range="dateRange"
        :documents="documents"
        @reset-app="resetApp"
        @back-to-topics="currentStep = 2"
      />

      <LoadingOverlay v-if="loading" />

      <ErrorMessage 
        v-if="error" 
        :error="error"
        @clear-error="clearError"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import axios from 'axios'
import DocumentUpload from './components/DocumentUpload.vue'
import AnalysisResults from './components/AnalysisResults.vue'
import DateRangeSelection from './components/DateRangeSelection.vue'
import SummaryReport from './components/SummaryReport.vue'
import LoadingOverlay from './components/LoadingOverlay.vue'
import ErrorMessage from './components/ErrorMessage.vue'

const API_BASE = 'http://localhost:8000/api'


const currentStep = ref(1)
const loading = ref(false)
const error = ref('')
const selectedTopic = ref('')
const topics = ref([])
const analysisSessionId = ref(null)
const summary = ref(null)
const documents = ref([])

const dateRange = reactive({
  start: '',
  end: ''
})


const canAnalyze = computed(() => {
  return documents.value.length > 0 && documents.value.every(doc => 
    doc.date && doc.theme.trim() && doc.text.trim()
  )
})

const canGenerateSummary = computed(() => {
  return dateRange.start && dateRange.end && selectedTopic.value
})


const addDocument = () => {
  documents.value.push({ date: '', theme: '', text: '' })
}

const removeDocument = (index) => {
  documents.value.splice(index, 1)
}

const clearAll = () => {
  documents.value = []
}


const loadExample = (exampleData) => {
  documents.value = JSON.parse(JSON.stringify(exampleData))
}


const selectTopic = (topicName) => {
  selectedTopic.value = topicName
}

const setDateRange = (range) => {
  const today = new Date()
  switch (range) {
    case 'lastWeek':
      const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
      dateRange.start = lastWeek.toISOString().split('T')[0]
      dateRange.end = today.toISOString().split('T')[0]
      break
    case 'lastMonth':
      const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate())
      dateRange.start = lastMonth.toISOString().split('T')[0]
      dateRange.end = today.toISOString().split('T')[0]
      break
    case 'all':
      if (documents.value.length > 0) {
        const dates = documents.value.map(doc => new Date(doc.date))
        const minDate = new Date(Math.min(...dates)).toISOString().split('T')[0]
        const maxDate = new Date(Math.max(...dates)).toISOString().split('T')[0]
        dateRange.start = minDate
        dateRange.end = maxDate
      }
      break
  }
}

const analyzeDocuments = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // Используем LLM endpoint
    const response = await axios.post(`${API_BASE}/llm/analyze-topics/`, {
      documents: {
        documents: documents.value
      },
      analysis_name: 'LLM Анализ документов'
    })

    topics.value = response.data.topic_statistics
    analysisSessionId.value = response.data.session_id
    currentStep.value = 2
    
    console.log("LLM Результаты анализа:", response.data)
    
  } catch (err) {

    console.warn("LLM недоступен, используем классический анализ:", err.message)
    
    try {
      const fallbackResponse = await axios.post(`${API_BASE}/analyze-topics/`, {
        documents: {
          documents: documents.value
        },
        analysis_name: 'Классический анализ',
        auto_determine_topics: true
      })
      
      topics.value = fallbackResponse.data.topic_statistics
      analysisSessionId.value = fallbackResponse.data.session_id
      currentStep.value = 2
      
    } catch (fallbackErr) {
      error.value = `Ошибка анализа: ${fallbackErr.response?.data?.error || fallbackErr.message}`
    }
  } finally {
    loading.value = false
  }
}

const nextStep = () => {
  currentStep.value = 3
}

const generateSummary = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // Используем LLM для генерации справки
    const response = await axios.post(`${API_BASE}/llm/generate-summary/`, {
      session_id: analysisSessionId.value,
      topic_name: selectedTopic.value,
      start_date: dateRange.start,
      end_date: dateRange.end
    })

 
    summary.value = {
      ...response.data,
      is_llm_generated: true
    }
    
    currentStep.value = 4
    
  } catch (err) {

    console.warn("LLM справка недоступна, используем простую:", err.message)
    
    try {
      const fallbackResponse = await axios.post(`${API_BASE}/summary-report/`, {
        session_id: analysisSessionId.value,
        start_date: dateRange.start,
        end_date: dateRange.end
      })

      summary.value = {
        ...fallbackResponse.data,
        is_llm_generated: false
      }
      
      currentStep.value = 4
      
    } catch (fallbackErr) {
      error.value = `Ошибка формирования справки: ${fallbackErr.response?.data?.error || fallbackErr.message}`
    }
  } finally {
    loading.value = false
  }
}

const resetApp = () => {
  currentStep.value = 1
  selectedTopic.value = ''
  documents.value = []
  topics.value = []
  analysisSessionId.value = null
  dateRange.start = ''
  dateRange.end = ''
  summary.value = null
  error.value = ''
}

const clearError = () => {
  error.value = ''
}
</script>

<style scoped>
.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-top: 20px;
  margin-bottom: 20px;
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
}

@media (max-width: 768px) {
  .container {
    margin: 10px;
    padding: 15px;
  }
}
</style>