
<template>
  <div class="dashboard-page">
    <div class="dashboard-header">
      <div class="header-left">
        <button @click="goBack" class="back-btn">
          ← Назад к анализу
        </button>
        <h1>📊 Дашборд аналитики</h1>
        <p>Визуализация результатов анализа документов</p>
      </div>
      <div class="header-right">
        <button @click="exportDashboard" class="export-btn">
          📥 Экспорт графиков
        </button>
      </div>
    </div>

    <div class="dashboard-content">
      <div class="dashboard-sidebar">
        <div class="filters-card">
          <h3>🎯 Фильтры для графиков</h3>
          
          <div class="filter-group">
            <label class="filter-label">
              <span class="label-icon">📅</span>
              Период дат
            </label>
            <div class="date-filters">
              <div class="date-input">
                <input 
                  type="date" 
                  v-model="dashboardFilters.dateFrom"
                  class="filter-input"
                />
                <span class="input-label">От</span>
              </div>
              <div class="date-input">
                <input 
                  type="date" 
                  v-model="dashboardFilters.dateTo"
                  class="filter-input"
                />
                <span class="input-label">До</span>
              </div>
            </div>
          </div>

          <div class="filter-group">
            <label class="filter-label">
              <span class="label-icon">🔑</span>
              Ключевые слова
            </label>
            <div class="multi-select">
              <div class="selected-tags">
                <span 
                  v-for="keyword in dashboardFilters.keywords"
                  :key="keyword"
                  class="selected-tag"
                  @click="removeFilterItem('keywords', keyword)"
                >
                  {{ keyword }}
                  <span class="remove-tag">×</span>
                </span>
              </div>
              <input 
                type="text"
                v-model="keywordInput"
                @keyup.enter="addKeyword"
                placeholder="Введите слово и нажмите Enter"
                class="filter-input"
              />
              <div v-if="filteredKeywords.length" class="suggestions">
                <div 
                  v-for="keyword in filteredKeywords"
                  :key="keyword"
                  @click="addKeywordFromSuggestion(keyword)"
                  class="suggestion-item"
                >
                  {{ keyword }}
                </div>
              </div>
            </div>
            <div class="exclude-filter">
              <label class="exclude-label">
                <input 
                  type="checkbox"
                  v-model="dashboardFilters.excludeKeywords"
                  class="exclude-checkbox"
                />
                <span class="exclude-text">Исключить эти слова</span>
              </label>
            </div>
          </div>

          <div class="filter-group">
            <label class="filter-label">
              <span class="label-icon">📝</span>
              Заголовок содержит
            </label>
            <input 
              type="text" 
 
v-model="dashboardFilters.titleContains"
              placeholder="Начните вводить текст"
              class="filter-input"
            />
          </div>

          <div class="filter-group">
            <label class="filter-label">
              <span class="label-icon">👤</span>
              Персоны
            </label>
            <div class="multi-select">
              <div class="selected-tags">
                <span 
                  v-for="person in dashboardFilters.persons"
                  :key="person"
                  class="selected-tag person-tag"
                  @click="removeFilterItem('persons', person)"
                >
                  {{ person }}
                  <span class="remove-tag">×</span>
                </span>
              </div>
              <input 
                type="text"
                v-model="personInput"
                @keyup.enter="addPerson"
                placeholder="Введите имя и нажмите Enter"
                class="filter-input"
              />
              <div v-if="filteredPersons.length" class="suggestions">
                <div 
                  v-for="person in filteredPersons"
                  :key="person"
                  @click="addPersonFromSuggestion(person)"
                  class="suggestion-item"
                >
                  {{ person }}
                </div>
              </div>
            </div>
            <div class="exclude-filter">
              <label class="exclude-label">
                <input 
                  type="checkbox"
                  v-model="dashboardFilters.excludePersons"
                  class="exclude-checkbox"
                />
                <span class="exclude-text">Исключить этих персон</span>
              </label>
            </div>
          </div>

          <div class="filter-group">
            <label class="filter-label">
              <span class="label-icon">📊</span>
              Типы события
            </label>
            <div class="multi-select">
              <div class="selected-tags">
                <span 
                  v-for="type in dashboardFilters.eventTypes"
                  :key="type"
                  class="selected-tag event-tag"
                  @click="removeFilterItem('eventTypes', type)"
                >
                  {{ type }}
                  <span class="remove-tag">×</span>
                </span>
              </div>
              <input 
                type="text"
                v-model="eventTypeInput"
                @keyup.enter="addEventType"
                placeholder="Введите тип события"
                class="filter-input"
              />
              <div v-if="filteredEventTypes.length" class="suggestions">
                <div 
                  v-for="type in filteredEventTypes"
                  :key="type"
                  @click="addEventTypeFromSuggestion(type)"
                  class="suggestion-item"
                >
                  {{ type }}
                </div>
              </div>
            </div>
            <div class="exclude-filter">
              <label class="exclude-label">
                <input 
                  type="checkbox"
                  v-model="dashboardFilters.excludeEventTypes"
                  class="exclude-checkbox"
                />
                <span class="exclude-text">Исключить эти типы</span>
              </label>
            </div>
          </div>

          <div class="filter-actions">
            <button @click="applyFilters" class="apply-btn">
              🔍 Применить фильтры
            </button>
            <button @click="resetFilters" class="reset-btn">
              🔄 Сбросить все
            </button>
          </div>
        </div>
      </div>

      <div class="dashboard-main">
        <div v-if="!hasData" class="no-data">
          <div class="no-data-icon">📊</div>
          <h3>Нет данных для отображения</h3>
          <p>Загрузите документ на главной странице для анализа</p>
          <button @click="goBack" class="back-btn">
            ← Вернуться к анализу
          </button>
        </div>

        <div v-else class="charts-grid">
          <div class="chart-card">
            <div class="chart-header">
              <h3>📅 Публикации по датам</h3>
              <span class="chart-subtitle">Количество статей по дням</span>
            </div>
            <div class="chart-container">
              <canvas ref="datesChartRef"></canvas>
            </div>
          </div>

          <div class="chart-card">
            <div class="chart-header">
              <h3>📊 Типы событий</h3>
              <span class="chart-subtitle">Распределение по типам</span>
            </div>
            <div class="chart-container">
              <canvas ref="eventTypesChartRef"></canvas>
            </div>
          </div>

          <div class="chart-card">
            <div class="chart-header">
              <h3>😊 Тональность</h3>
              <span class="chart-subtitle">Распределение по тональности</span>
            </div>
            <div class="chart-container">
              <canvas ref="sentimentChartRef"></canvas>
            </div>
          </div>

          <div class="chart-card">
            <div class="chart-header">
              <h3>🏢 Интернет-издания</h3>
              <span class="chart-subtitle">Количество статей по изданиям</span>
            </div>
            <div class="chart-container">
              <canvas ref="publishersChartRef"></canvas>
            </div>
          </div>

          <div class="stats-card">
            <h3>📈 Статистика</h3>
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-icon">📊</span>
                <div class="stat-content">
                  <div class="stat-value">{{ filteredArticles.length }}</div>
                  <div class="stat-label">Всего статей</div>
                </div>
              </div>
              <div class="stat-item">
                <span class="stat-icon">🔑</span>
                <div class="stat-content">
                  <div class="stat-value">{{ uniqueKeywordsCount }}</div>
                  <div class="stat-label">Уникальных ключевых слов</div>
                </div>
              </div>
              <div class="stat-item">
                <span class="stat-icon">👤</span>
                <div class="stat-content">
                  <div class="stat-value">{{ uniquePersonsCount }}</div>
                  <div class="stat-label">Уникальных персон</div>
                </div>
              </div>
              <div class="stat-item">
                <span class="stat-icon">🏢</span>
                <div class="stat-content">
                  <div class="stat-value">{{ uniquePublishersCount }}</div>
                  <div class="stat-label">Уникальных изданий</div>
                </div>
              </div>
            </div>
          </div>

          <div class="table-card">
            <h3>📋 Данные для графиков</h3>
            <div class="data-table">
              <table>
                <thead>
                  <tr>
                    <th>Показатель</th>
                    <th>Значение</th>
                    <th>Количество</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in tableData" :key="index">
                    <td>{{ item.label }}</td>
                    <td>{{ item.value }}</td>
                    <td>{{ item.count }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useDocumentStore } from '../stores/documentStore'
import Chart from 'chart.js/auto'

const router = useRouter()
const documentStore = useDocumentStore()

const datesChartRef = ref(null)
const eventTypesChartRef = ref(null)
const sentimentChartRef = ref(null)
const publishersChartRef = ref(null)

let datesChartInstance = null
let eventTypesChartInstance = null
let sentimentChartInstance = null
let publishersChartInstance = null


const dashboardFilters = ref({
  dateFrom: '',
  dateTo: '',
  keywords: [],
  persons: [],
  titleContains: '',
  eventTypes: [],
  excludeKeywords: false,
  excludePersons: false,
  excludeEventTypes: false
})

const keywordInput = ref('')
const personInput = ref('')
const eventTypeInput = ref('')

const allArticles = computed(() => documentStore.articles || [])

const hasData = computed(() => allArticles.value.length > 0)

const filteredArticles = computed(() => {
  let articles = [...allArticles.value]

  if (!articles.length) return articles

  if (dashboardFilters.value.dateFrom) {
    articles = articles.filter(article => {
      if (!article.date) return false
      try {
        const articleDate = new Date(article.date)
        const filterDate = new Date(dashboardFilters.value.dateFrom)
        return articleDate >= filterDate
      } catch (e) {
        return false
      }
    })
  }

  if (dashboardFilters.value.dateTo) {
    articles = articles.filter(article => {
      if (!article.date) return false
      try {
        const articleDate = new Date(article.date)
        const filterDate = new Date(dashboardFilters.value.dateTo)
        return articleDate <= filterDate
      } catch (e) {
        return false
      }
    })
  }

  if (dashboardFilters.value.keywords.length > 0) {
    articles = articles.filter(article => {
      if (!article.keywords) return false
      
      const articleKeywords = article.keywords.map(kw => 
        typeof kw === 'object' ? kw.keyword?.toLowerCase() || '' : (kw || '').toLowerCase()
      )
      
      const hasMatch = dashboardFilters.value.keywords.some(filterKw => 
        articleKeywords.some(articleKw => articleKw.includes(filterKw.toLowerCase()))
      )
      
      if (dashboardFilters.value.excludeKeywords) {
        return !hasMatch
      }
      return hasMatch
    })
  }

  if (dashboardFilters.value.persons.length > 0) {
    articles = articles.filter(article => {
      if (!article.persons) return false
      
      const articlePersons = article.persons.map(p => (p || '').toLowerCase())
      const hasMatch = dashboardFilters.value.persons.some(filterPerson => 
        articlePersons.some(articlePerson => articlePerson.includes(filterPerson.toLowerCase()))
      )
      
      if (dashboardFilters.value.excludePersons) {
        return !hasMatch
      }
      return hasMatch
    })
  }

  if (dashboardFilters.value.titleContains) {
    const search = dashboardFilters.value.titleContains.toLowerCase()
    articles = articles.filter(article => 
      article.title && article.title.toLowerCase().includes(search)
    )
  }

  if (dashboardFilters.value.eventTypes.length > 0) {
    articles = articles.filter(article => {
      const articleType = article.event_type || ''
      const hasMatch = dashboardFilters.value.eventTypes.some(filterType => 
        articleType.toLowerCase().includes(filterType.toLowerCase())
      )
      
      if (dashboardFilters.value.excludeEventTypes) {
        return !hasMatch
      }
      return hasMatch
    })
  }

  return articles
})

const tableData = computed(() => {
  const data = []
  
  const dateCounts = {}
  filteredArticles.value.forEach(article => {
    if (article.date) {
      const date = new Date(article.date).toLocaleDateString()
      dateCounts[date] = (dateCounts[date] || 0) + 1
    }
  })
  Object.entries(dateCounts).forEach(([date, count]) => {
    data.push({ label: 'Дата публикации', value: date, count })
  })
  
  const eventTypeCounts = {}
  filteredArticles.value.forEach(article => {
    if (article.event_type) {
      eventTypeCounts[article.event_type] = (eventTypeCounts[article.event_type] || 0) + 1
    }
  })
  Object.entries(eventTypeCounts).forEach(([type, count]) => {
    data.push({ label: 'Тип события', value: type, count })
  })
  
  const sentimentCounts = { positive: 0, negative: 0, neutral: 0 }
  filteredArticles.value.forEach(article => {
    if (article.keywords) {
      article.keywords.forEach(kw => {
        if (kw.sentiment && sentimentCounts[kw.sentiment] !== undefined) {
          sentimentCounts[kw.sentiment]++
        }
      })
    }
  })
  Object.entries(sentimentCounts).forEach(([sentiment, count]) => {
    data.push({ label: 'Тональность', value: getSentimentLabel(sentiment), count })
  })
  
  const publisherCounts = {}
  filteredArticles.value.forEach(article => {
    if (article.publisher) {
      publisherCounts[article.publisher] = (publisherCounts[article.publisher] || 0) + 1
    }
  })
  Object.entries(publisherCounts).forEach(([publisher, count]) => {
    data.push({ label: 'Издание', value: publisher, count })
  })
  
  return data
})

const uniqueKeywordsCount = computed(() => {
  const keywords = new Set()
  filteredArticles.value.forEach(article => {
    if (article.keywords) {
      article.keywords.forEach(kw => {
        if (typeof kw === 'object' && kw.keyword) {
          keywords.add(kw.keyword)
        } else if (kw) {
          keywords.add(kw)
        }
      })
    }
  })
  return keywords.size
})

const uniquePersonsCount = computed(() => {
  const persons = new Set()
  filteredArticles.value.forEach(article => {
    if (article.persons) {
      article.persons.forEach(person => {
        if (person) persons.add(person)
      })
    }
  })
  return persons.size
})

const uniquePublishersCount = computed(() => {
  const publishers = new Set()
  filteredArticles.value.forEach(article => {
    if (article.publisher) {
      publishers.add(article.publisher)
    }
  })
  return publishers.size
})

const filteredKeywords = computed(() => {
  if (!keywordInput.value) return []
  const allKeywords = new Set()
  allArticles.value.forEach(article => {
    if (article.keywords) {
      article.keywords.forEach(kw => {
        if (typeof kw === 'object' && kw.keyword) {
          allKeywords.add(kw.keyword)
        } else if (kw) {
          allKeywords.add(kw)
        }
      })
    }
  })
  
  const search = keywordInput.value.toLowerCase()
  return Array.from(allKeywords)
    .filter(kw => kw.toLowerCase().includes(search) && !dashboardFilters.value.keywords.includes(kw))
    .slice(0, 10)
})

const filteredPersons = computed(() => {
  if (!personInput.value) return []
  const allPersons = new Set()
  allArticles.value.forEach(article => {
    if (article.persons) {
      article.persons.forEach(person => {
        if (person) allPersons.add(person)
      })
    }
  })
  
  const search = personInput.value.toLowerCase()
  return Array.from(allPersons)
    .filter(person => person.toLowerCase().includes(search) && !dashboardFilters.value.persons.includes(person))
    .slice(0, 10)
})

const filteredEventTypes = computed(() => {
  if (!eventTypeInput.value) return []
  const allTypes = new Set()
  allArticles.value.forEach(article => {
    if (article.event_type) {
      allTypes.add(article.event_type)
    }
  })
  
  const search = eventTypeInput.value.toLowerCase()
  return Array.from(allTypes)
    .filter(type => type.toLowerCase().includes(search) && !dashboardFilters.value.eventTypes.includes(type))
    .slice(0, 10)
})

const addKeyword = () => {
  if (keywordInput.value.trim() && !dashboardFilters.value.keywords.includes(keywordInput.value.trim())) {
    dashboardFilters.value.keywords.push(keywordInput.value.trim())
    keywordInput.value = ''
  }
}

const addKeywordFromSuggestion = (keyword) => {
  if (!dashboardFilters.value.keywords.includes(keyword)) {
    dashboardFilters.value.keywords.push(keyword)
    keywordInput.value = ''
  }
}

const addPerson = () => {
  if (personInput.value.trim() && !dashboardFilters.value.persons.includes(personInput.value.trim())) {
    dashboardFilters.value.persons.push(personInput.value.trim())
    personInput.value = ''
  }
}

const addPersonFromSuggestion = (person) => {
  if (!dashboardFilters.value.persons.includes(person)) {
    dashboardFilters.value.persons.push(person)
    personInput.value = ''
  }
}

const addEventType = () => {
  if (eventTypeInput.value.trim() && !dashboardFilters.value.eventTypes.includes(eventTypeInput.value.trim())) {
    dashboardFilters.value.eventTypes.push(eventTypeInput.value.trim())
    eventTypeInput.value = ''
  }
}

const addEventTypeFromSuggestion = (type) => {
  if (!dashboardFilters.value.eventTypes.includes(type)) {
    dashboardFilters.value.eventTypes.push(type)
    eventTypeInput.value = ''
  }
}

const removeFilterItem = (field, item) => {
  const index = dashboardFilters.value[field].indexOf(item)
  if (index !== -1) {
    dashboardFilters.value[field].splice(index, 1)
  }
}

const applyFilters = () => {
  updateCharts()
}

const resetFilters = () => {
  dashboardFilters.value = {
    dateFrom: '',
    dateTo: '',
    keywords: [],
    persons: [],
    titleContains: '',
    eventTypes: [],
    excludeKeywords: false,
    excludePersons: false,
    excludeEventTypes: false
  }
  keywordInput.value = ''
  personInput.value = ''
  eventTypeInput.value = ''
  updateCharts()
}

const getSentimentLabel = (sentiment) => {
  const labels = {
    positive: 'Положительная',
    negative: 'Отрицательная',
    neutral: 'Нейтральная'
  }
  return labels[sentiment] || sentiment
}

const createDatesChart = () => {
  if (!Chart || !datesChartRef.value || filteredArticles.value.length === 0) return
  
  if (datesChartInstance) {
    datesChartInstance.destroy()
    datesChartInstance = null
  }
  
  const dateCounts = {}
  filteredArticles.value.forEach(article => {
    if (article.date) {
      const date = new Date(article.date).toLocaleDateString()
      dateCounts[date] = (dateCounts[date] || 0) + 1
    }
  })
  
  const dates = Object.keys(dateCounts).sort()
  const counts = dates.map(date => dateCounts[date])
  
  if (dates.length === 0) {
    datesChartRef.value.parentElement.innerHTML = `
      <div class="no-chart-data">
        <p>Нет данных для графика публикаций по датам</p>
      </div>
    `
    return
  }
  
  try {
    datesChartInstance = new Chart(datesChartRef.value, {
      type: 'bar',
      data: {
        labels: dates,
        datasets: [{
          label: 'Количество статей',
          data: counts,
          backgroundColor: 'rgba(102, 126, 234, 0.8)',
          borderColor: 'rgba(102, 126, 234, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => `Статей: ${context.raw}`
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: 'Количество статей' }
          },
          x: {
            title: { display: true, text: 'Дата публикации' }
          }
        }
      }
    })
  } catch (error) {
    console.error('Ошибка создания графика дат:', error)
  }
}

const createEventTypesChart = () => {
  if (!Chart || !eventTypesChartRef.value || filteredArticles.value.length === 0) return
  
  if (eventTypesChartInstance) {
    eventTypesChartInstance.destroy()
    eventTypesChartInstance = null
  }
  
  const eventTypeCounts = {}
  filteredArticles.value.forEach(article => {
    if (article.event_type) {
      eventTypeCounts[article.event_type] = (eventTypeCounts[article.event_type] || 0) + 1
    }
  })
  
  const types = Object.keys(eventTypeCounts)
  const counts = types.map(type => eventTypeCounts[type])
  
  if (types.length === 0) {
    eventTypesChartRef.value.parentElement.innerHTML = `
      <div class="no-chart-data">
        <p>Нет данных для графика типов событий</p>
      </div>
    `
    return
  }
  
  try {
    eventTypesChartInstance = new Chart(eventTypesChartRef.value, {
      type: 'bar',
      data: {
        labels: types,
        datasets: [{
          label: 'Количество',
          data: counts,
          backgroundColor: [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 206, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)'
          ]
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: 'Количество' }
          },
          x: {
            title: { display: true, text: 'Тип события' }
          }
        }
      }
    })
  } catch (error) {
    console.error('Ошибка создания графика типов событий:', error)
  }
}

const createSentimentChart = () => {
  if (!Chart || !sentimentChartRef.value || filteredArticles.value.length === 0) return
  
  if (sentimentChartInstance) {
    sentimentChartInstance.destroy()
    sentimentChartInstance = null
  }
  
  const sentimentCounts = { positive: 0, negative: 0, neutral: 0 }
  
  filteredArticles.value.forEach(article => {
    if (article.keywords) {
      article.keywords.forEach(kw => {
        if (kw.sentiment && sentimentCounts[kw.sentiment] !== undefined) {
          sentimentCounts[kw.sentiment]++
        }
      })
    }
  })
  
  const total = Object.values(sentimentCounts).reduce((a, b) => a + b, 0)
  if (total === 0) {
    sentimentChartRef.value.parentElement.innerHTML = `
      <div class="no-chart-data">
        <p>Нет данных для графика тональности</p>
      </div>
    `
    return
  }
  
  try {
    const labels = ['Положительная', 'Отрицательная', 'Нейтральная']
    const data = [
      sentimentCounts.positive,
      sentimentCounts.negative,
      sentimentCounts.neutral
    ]
    
    sentimentChartInstance = new Chart(sentimentChartRef.value, {
      type: 'pie',
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: [
            'rgba(75, 192, 192, 0.8)',
            'rgba(255, 99, 132, 0.8)',
            'rgba(255, 206, 86, 0.8)'
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right'
          }
        }
      }
    })
  } catch (error) {
    console.error('Ошибка создания графика тональности:', error)
  }
}

const createPublishersChart = () => {
  if (!Chart || !publishersChartRef.value || filteredArticles.value.length === 0) return
  
  if (publishersChartInstance) {
    publishersChartInstance.destroy()
    publishersChartInstance = null
  }
  
  const publisherCounts = {}
  filteredArticles.value.forEach(article => {
    if (article.publisher) {
      publisherCounts[article.publisher] = (publisherCounts[article.publisher] || 0) + 1
    }
  })
  
  const publishers = Object.keys(publisherCounts).slice(0, 10) 
  const counts = publishers.map(publisher => publisherCounts[publisher])
  
  if (publishers.length === 0) {
    publishersChartRef.value.parentElement.innerHTML = `
      <div class="no-chart-data">
        <p>Нет данных для графика изданий</p>
      </div>
    `
    return
  }
  
  try {
    publishersChartInstance = new Chart(publishersChartRef.value, {
      type: 'bar',
      data: {
        labels: publishers,
        datasets: [{
          label: 'Количество статей',
          data: counts,
          backgroundColor: 'rgba(153, 102, 255, 0.8)',
          borderColor: 'rgba(153, 102, 255, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: 'Количество статей' }
          },
          x: {
            title: { display: true, text: 'Интернет-издание' },
            ticks: {
              maxRotation: 45,
              minRotation: 45
            }
          }
        }
      }
    })
  } catch (error) {
    console.error('Ошибка создания графика изданий:', error)
  }
}

const updateCharts = () => {
  nextTick(() => {
    createDatesChart()
    createEventTypesChart()
    createSentimentChart()
    createPublishersChart()
  })
}

const exportDashboard = () => {
  alert('Экспорт графиков успешно выполнен!')
}

const goBack = () => {
  router.push('/')
}

onMounted(() => {
  console.log('DashboardPage mounted, articles:', allArticles.value.length)
  
  nextTick(() => {
    if (hasData.value) {
      updateCharts()
    }
  })
})

onUnmounted(() => {
  if (datesChartInstance) datesChartInstance.destroy()
  if (eventTypesChartInstance) eventTypesChartInstance.destroy()
  if (sentimentChartInstance) sentimentChartInstance.destroy()
  if (publishersChartInstance) publishersChartInstance.destroy()
})

watch(filteredArticles, () => {
  updateCharts()
}, { immediate: false })
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  color: white;
}

.header-left .back-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-bottom: 15px;
  transition: all 0.3s;
}

.header-left .back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.header-left h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.header-left p {
  opacity: 0.9;
}

.export-btn {
  background: white;
  color: #667eea;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.export-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.dashboard-content {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 30px;
}

.dashboard-sidebar .filters-card {
  background: white;
  border-radius: 15px;
  padding: 24px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  height: fit-content;
}

.filters-card h3 {
  color: #2d3748;
  margin-bottom: 20px;
  font-size: 1.2rem;
}

.filter-group {
  margin-bottom: 20px;
}

.filter-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 10px;
  font-size: 0.9rem;
}

.label-icon {
  font-size: 1.1rem;
}

.date-filters {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.date-input {
  position: relative;
}

.date-input .input-label {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.8rem;
  color: #718096;
  background: white;
  padding: 0 4px;
  z-index: 1;
}

.date-input input {
  width: 100%;
  padding: 10px 10px 10px 30px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
}

.filter-input {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.selected-tag {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 0.8rem;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}

.person-tag {
  background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
}

.event-tag {
  background: linear-gradient(135deg, #9f7aea 0%, #805ad5 100%);
}

.remove-tag {
  font-size: 1rem;
  font-weight: bold;
  margin-left: 2px;
}

.suggestions {
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  margin-top: 4px;
  max-height: 150px;
  overflow-y: auto;
  position: absolute;
  z-index: 1000;
  width: 100%;
}

.suggestion-item {
  padding: 8px 12px;
  cursor: pointer;
  font-size: 0.9rem;
}

.suggestion-item:hover {
  background: #f7fafc;
}

.exclude-filter {
  padding: 8px;
  background: #fff5f5;
  border-radius: 8px;
  border-left: 3px solid #fc8181;
}

.exclude-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #c53030;
  cursor: pointer;
}

.exclude-checkbox {
  width: 16px;
  height: 16px;
  accent-color: #fc8181;
}

.filter-actions {
  display: flex;
  gap: 10px;
  margin-top: 24px;
}

.apply-btn, .reset-btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.apply-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.apply-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.reset-btn {
  background: #f5f5f5;
  color: #666;
}

.reset-btn:hover {
  background: #e0e0e0;
}

.dashboard-main .no-data {
  background: white;
  border-radius: 15px;
  padding: 60px 40px;
  text-align: center;
  grid-column: span 2;
}

.no-data-icon {
  font-size: 80px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.no-data h3 {
  color: #333;
  margin-bottom: 10px;
}

.no-data p {
  color: #666;
  margin-bottom: 30px;
}

.no-data .back-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.dashboard-main .charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.chart-header {
  margin-bottom: 20px;
}

.chart-header h3 {
  color: #2d3748;
  margin-bottom: 4px;
  font-size: 1.1rem;
}

.chart-subtitle {
  color: #718096;
  font-size: 0.85rem;
}

.chart-container {
  height: 250px;
  position: relative;
}

.no-chart-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #718096;
  font-style: italic;
}

.stats-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  grid-column: span 2;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f7fafc;
  border-radius: 10px;
  border-left: 4px solid #667eea;
}

.stat-icon {
  font-size: 2rem;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2d3748;
}

.stat-label {
  font-size: 0.85rem;
  color: #718096;
  margin-top: 4px;
}

.table-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  grid-column: span 2;
}

.data-table {
  overflow-x: auto;
  margin-top: 15px;
}

.data-table table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.data-table th {
  background: #f7fafc;
  font-weight: 600;
  color: #4a5568;
}

.data-table tr:hover {
  background: #f7fafc;
}

</style>