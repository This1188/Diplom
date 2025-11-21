<template>
  <div id="app">
    <div class="container">
      <h1>Анализатор текстовых данных</h1>
      
      <!-- Шаг 1: Загрузка данных -->
      <div v-if="currentStep === 1" class="step">
        <h2>Шаг 1: Загрузка текстовых данных</h2>
        
        <div class="upload-section">
          <div class="upload-options">
            <button @click="loadExample" class="example-btn">📋 Показать пример</button>
            <button @click="clearAll" class="clear-btn">❌ Очистить все</button>
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
              @click="removeDocument(index)"
              class="remove-btn"
              v-if="documents.length > 1"
            >×</button>
          </div>
          
          <button @click="addDocument" class="add-btn">+ Добавить документ</button>
          
          <div class="documents-count">
            Всего документов: {{ documents.length }}
          </div>
          
          <button @click="analyzeDocuments" class="analyze-btn" :disabled="!canAnalyze">
            Анализировать документы
          </button>
        </div>
      </div>

      <!-- Шаг 2: Результаты анализа и выбор темы -->
      <div v-if="currentStep === 2" class="step">
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
              @click="selectTopic(topic.topic_name)"
            >
              <h4>{{ topic.topic_name }}</h4>
              <p>Документов: {{ topic.document_count }}</p>
              <p>Ключевые слова: {{ topic.keywords.slice(0, 3).join(', ') }}...</p>
            </div>
          </div>
          
          <button @click="nextStep" class="next-btn" :disabled="!selectedTopic">
            Выбрать временной диапазон
          </button>
        </div>
      </div>

      <!-- Шаг 3: Выбор временного диапазона -->
      <div v-if="currentStep === 3" class="step">
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
            <button @click="setDateRange('lastWeek')" class="suggestion-btn">За последнюю неделю</button>
            <button @click="setDateRange('lastMonth')" class="suggestion-btn">За последний месяц</button>
            <button @click="setDateRange('all')" class="suggestion-btn">Весь период</button>
          </div>
          
          <button @click="generateSummary" class="generate-btn" :disabled="!canGenerateSummary">
            Сформировать справку
          </button>
        </div>
      </div>

      <!-- Шаг 4: Справка -->
      <div v-if="currentStep === 4" class="step">
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
          <button @click="resetApp" class="reset-btn">Начать новый анализ</button>
          <button @click="currentStep = 2" class="back-btn">Вернуться к выбору темы</button>
        </div>
      </div>

      <!-- Индикатор загрузки -->
      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
        <p>Обработка данных...</p>
      </div>

      <!-- Сообщения об ошибках -->
      <div v-if="error" class="error-message">
        {{ error }}
        <button @click="clearError" class="close-error">×</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

// Reactive state
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

// Примерные данные (10 статей про хоккей)
const exampleData = [
  {
    "date": "2024-03-01",
    "theme": "Хоккейный матч",
    "text": "Вчера состоялся захватывающий матч между командами Спартак и ЦСКА. Игра закончилась со счетом 3:2 в пользу Спартака. Лучшим игроком матча был признан вратарь, отразивший 35 бросков по воротам."
  },
  {
    "date": "2024-03-02",
    "theme": "Хоккейные события",
    "text": "Драматическая победа Ак Барса над СКА в овертайме. Команда из Казани сумела отыграться за две минуты до конца третьего периода и победила в дополнительное время. Хет-трик оформил капитан команды."
  },
  {
    "date": "2024-03-03",
    "theme": "Хоккейные травмы",
    "text": "Травма ключевого нападающего Динамо может повлиять на исход плей-офф. Врачи диагностируют повреждение колена, восстановление займет не менее шести недель. Тренерский штаб ищет замену в составе."
  },
  {
    "date": "2024-03-04",
    "theme": "Хоккейные дебюты",
    "text": "Молодой вратарь Автомобилиста дебютировал в КХЛ и сразу сделал шатаут. 20-летний голкипер отразил все 28 бросков по своим воротам и помог команде одержать победу со счетом 1:0."
  },
  {
    "date": "2024-03-05",
    "theme": "Хоккейные рекорды",
    "text": "Рекорд посещаемости на матче Локомотив - Салават Юлаев. Более 12 тысяч зрителей стали свидетелями семиголевой победной игры. Обе команды показали атакующий хоккей высшего класса."
  },
  {
    "date": "2024-03-06",
    "theme": "Хоккейные скандалы",
    "text": "Скандал с судейством в матче Трактор - Металлург. Главный тренер проигравшей команды заявил о необъективном арбитраже. Лига начала официальное расследование инцидента."
  },
  {
    "date": "2024-03-07",
    "theme": "Хоккейные трансферы",
    "text": "Канадский легионер адаптируется к российскому чемпионату. Нападающий рассказал о различиях в стиле игры и сложностях акклиматизации. Болельщики тепло принимают нового игрока."
  },
  {
    "date": "2024-03-08",
    "theme": "Хоккейные сборы",
    "text": "Подготовка к чемпионату мира начинается со сбора национальной команды. Главный тренер объявил расширенный список из 40 игроков. Окончательный состав будет определен после плей-офф КХЛ."
  },
  {
    "date": "2024-03-09",
    "theme": "Хоккейная инфраструктура",
    "text": "Реконструкция ледового дворца завершится к следующему сезону. Обновленная арена будет вмещать на 3 тысячи зрителей больше и получит современное медиаоснащение. Смета проекта превысила 2 миллиарда рублей."
  },
  {
    "date": "2024-03-10",
    "theme": "Хоккейные карьеры",
    "text": "Легендарный защитник завершает карьеру в возрасте 42 лет. Ветеран сыграл более 1000 матчей в КХЛ и выиграл три Кубка Гагарина. Клуб планирует провести торжественную церемонию прощания."
  }
]

// Computed properties
const canAnalyze = computed(() => {
  return documents.value.length > 0 && documents.value.every(doc => 
    doc.date && doc.theme.trim() && doc.text.trim()
  )
})

const canGenerateSummary = computed(() => {
  return dateRange.start && dateRange.end && selectedTopic.value
})

// Methods
const addDocument = () => {
  documents.value.push({ date: '', theme: '', text: '' })
}

const removeDocument = (index) => {
  documents.value.splice(index, 1)
}

const clearAll = () => {
  documents.value = []
}

const loadExample = () => {
  documents.value = JSON.parse(JSON.stringify(exampleData))
}

const selectTopic = (topicName) => {
  selectedTopic.value = topicName
}

const getSelectedTopicKeywords = () => {
  const topic = topics.value.find(t => t.topic_name === selectedTopic.value)
  return topic ? topic.keywords : []
}

const getSelectedTopicDocumentCount = () => {
  const topic = topics.value.find(t => t.topic_name === selectedTopic.value)
  return topic ? topic.document_count : 0
}

const getSelectedTopicConfidence = () => {
  const topic = topics.value.find(t => t.topic_name === selectedTopic.value)
  return topic ? topic.average_confidence : 0
}

const getFilteredDocuments = () => {
  if (!dateRange.start || !dateRange.end) return []
  
  return documents.value.filter(doc => {
    const docDate = new Date(doc.date)
    const startDate = new Date(dateRange.start)
    const endDate = new Date(dateRange.end)
    return docDate >= startDate && docDate <= endDate
  })
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
    const response = await axios.post(`${API_BASE}/analyze-topics/`, {
      documents: {
        documents: documents.value
      },
      analysis_name: 'Анализ документов',
      auto_determine_topics: true
    })

    topics.value = response.data.topic_statistics
    analysisSessionId.value = response.data.session_id
    currentStep.value = 2
    
  } catch (err) {
    error.value = `Ошибка анализа: ${err.response?.data?.error || err.message}`
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
    const response = await axios.post(`${API_BASE}/summary-report/`, {
      session_id: analysisSessionId.value,
      start_date: dateRange.start,
      end_date: dateRange.end
    })

    summary.value = response.data
    currentStep.value = 4
    
  } catch (err) {
    error.value = `Ошибка формирования справки: ${err.response?.data?.error || err.message}`
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

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  z-index: 1000;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

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

@media (max-width: 768px) {
  .document-row {
    grid-template-columns: 1fr;
  }
  
  .date-inputs {
    flex-direction: column;
    align-items: center;
  }
  
  .date-suggestions {
    flex-direction: column;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .container {
    margin: 10px;
    padding: 15px;
  }
  
  .themes-grid {
    grid-template-columns: 1fr;
  }
}
</style>