<template>
  <div class="filters-panel">
    <div class="filters-header">
      <h3>🎯 Фильтры</h3>
      <div class="header-buttons">
        <button 
          @click="applyFilters"
          class="apply-btn"
          :class="{ disabled: !hasFilterChanges }"
          :disabled="!hasFilterChanges"
        >
          Применить
        </button>
        <button 
          @click="resetAllFilters"
          class="reset-btn"
          :class="{ disabled: !hasActiveFilters }"
          :disabled="!hasActiveFilters"
        >
          Сбросить все
        </button>
      </div>
    </div>

    <div class="filters-content">
      <div class="filter-group">
        <label class="filter-label">
          <span class="label-icon">📅</span>
          Период дат
        </label>
        <div class="date-filters">
          <div class="date-input-wrapper">
            <div class="date-input">
              <input 
                type="date" 
                v-model="localFilters.dateFrom"
                class="filter-input"
                @change="markAsChanged"
                :max="localFilters.dateTo"
              />
              <span class="input-label">От</span>
            </div>
          </div>
          <div class="date-input-wrapper">
            <div class="date-input">
              <input 
                type="date" 
                v-model="localFilters.dateTo"
                class="filter-input"
                @change="markAsChanged"
                :min="localFilters.dateFrom"
              />
              <span class="input-label">До</span>
            </div>
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
              v-for="keyword in localFilters.keywords"
              :key="keyword.keyword || keyword"
              class="selected-tag"
              @click="removeKeyword(keyword)"
            >
              {{ typeof keyword === 'object' ? keyword.keyword : keyword }}
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
              :key="keyword.keyword"
              @click="selectKeyword(keyword)"
              class="suggestion-item"
            >
              <span>{{ keyword.keyword }}</span>
              <span class="sentiment-badge" :class="keyword.sentiment">
                {{ getSentimentIcon(keyword.sentiment) }}
              </span>
            </div>
          </div>
        </div>
        <div class="exclude-filter">
          <label class="exclude-label">
            <input 
              type="checkbox"
              v-model="localFilters.excludeKeywords"
              @change="markAsChanged"
              class="exclude-checkbox"
            />
            <span class="exclude-text">Исключить эти слова</span>
          </label>
        </div>
      </div>

      <div class="filter-group">
        <label class="filter-label">
          <span class="label-icon">👤</span>
          Персоны
        </label>
        <div class="multi-select">
          <div class="selected-tags">
            <span 
              v-for="person in localFilters.persons"
              :key="person"
              class="selected-tag person-tag"
              @click="removePerson(person)"
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
              @click="selectPerson(person)"
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
              v-model="localFilters.excludePersons"
              @change="markAsChanged"
              class="exclude-checkbox"
            />
            <span class="exclude-text">Исключить этих персон</span>
          </label>
        </div>
      </div>

      <div class="filter-group">
        <label class="filter-label">
          <span class="label-icon">✍️</span>
          Авторы
        </label>
        <div class="multi-select">
          <div class="selected-tags">
            <span 
              v-for="author in localFilters.authors"
              :key="author"
              class="selected-tag author-tag"
              @click="removeAuthor(author)"
            >
              {{ author }}
              <span class="remove-tag">×</span>
            </span>
          </div>
          <input 
            type="text"
            v-model="authorInput"
            @keyup.enter="addAuthor"
            placeholder="Введите автора и нажмите Enter"
            class="filter-input"
          />
          <div v-if="filteredAuthors.length" class="suggestions">
            <div 
              v-for="author in filteredAuthors"
              :key="author"
              @click="selectAuthor(author)"
              class="suggestion-item"
            >
              {{ author }}
            </div>
          </div>
        </div>
        <div class="exclude-filter">
          <label class="exclude-label">
            <input 
              type="checkbox"
              v-model="localFilters.excludeAuthors"
              @change="markAsChanged"
              class="exclude-checkbox"
            />
            <span class="exclude-text">Исключить этих авторов</span>
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
          v-model="localFilters.titleContains"
          @input="markAsChanged"
          placeholder="Начните вводить текст"
          class="filter-input"
        />
      </div>

      <div class="filter-group">
        <label class="filter-label">
          <span class="label-icon">📊</span>
          Тип события
        </label>
        <div class="multi-select">
          <div class="selected-tags">
            <span 
              v-for="type in localFilters.eventType"
              :key="type"
              class="selected-tag event-tag"
              @click="removeEventType(type)"
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
              @click="selectEventType(type)"
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
              v-model="localFilters.excludeEventTypes"
              @change="markAsChanged"
              class="exclude-checkbox"
            />
            <span class="exclude-text">Исключить эти типы</span>
          </label>
        </div>
      </div>

      <div class="filter-group">
        <label class="filter-label">
          <span class="label-icon">😊</span>
          Тональность
        </label>
        <div class="sentiment-filters">
          <button 
            v-for="sentiment in sentimentOptions"
            :key="sentiment.value"
            @click="toggleSentiment(sentiment.value)"
            :class="[
              'sentiment-btn',
              sentiment.value,
              { active: localFilters.sentiment === sentiment.value }
            ]"
            :title="sentiment.label"
          >
            <span class="sentiment-icon">{{ sentiment.icon }}</span>
            <span class="sentiment-label">{{ sentiment.label }}</span>
          </button>
        </div>
      </div>

      <div class="filter-group">
        <label class="filter-label">
          <span class="label-icon">📈</span>
          Сортировка
        </label>
        <select 
          v-model="localFilters.sortBy"
          @change="markAsChanged"
          class="filter-select"
        >
          <option value="date">По дате (новые сначала)</option>
          <option value="relevance">По релевантности</option>
          <option value="title">По заголовку (А-Я)</option>
          <option value="length">По длине текста</option>
        </select>
      </div>

      <div class="active-filters" v-if="hasActiveFilters">
        <h4>Активные фильтры:</h4>
        <div class="active-tags">
          <span 
            v-for="filter in activeFilterTags" 
            :key="filter.key"
            class="active-tag"
            @click="removeFilter(filter.key)"
          >
            {{ filter.label }}
            <span class="remove-tag">×</span>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({})
  },
  articles: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:filters', 'reset'])

const localFilters = ref({
  dateFrom: '',
  dateTo: '',
  keywords: [],
  persons: [],
  authors: [],
  titleContains: '',
  eventType: [],
  sentiment: '',
  sortBy: 'date',
  excludeKeywords: false,
  excludePersons: false,
  excludeAuthors: false,
  excludeEventTypes: false
})

const hasFilterChanges = ref(false)

const keywordInput = ref('')
const personInput = ref('')
const authorInput = ref('')
const eventTypeInput = ref('')

const sentimentOptions = [
  { value: 'positive', label: 'Положительная', icon: '😊' },
  { value: 'negative', label: 'Отрицательная', icon: '😠' },
  { value: 'neutral', label: 'Нейтральная', icon: '😐' }
]

const allKeywords = computed(() => {
  const keywordsMap = new Map()
  props.articles.forEach(article => {
    if (article.keywords && Array.isArray(article.keywords)) {
      article.keywords.forEach(kw => {
        if (kw && kw.keyword) {
          if (!keywordsMap.has(kw.keyword)) {
            keywordsMap.set(kw.keyword, {
              keyword: kw.keyword,
              sentiment: kw.sentiment || 'neutral'
            })
          }
        }
      })
    }
  })
  return Array.from(keywordsMap.values())
})

const allPersons = computed(() => {
  const persons = new Set()
  props.articles.forEach(article => {
    if (article.persons && Array.isArray(article.persons)) {
      article.persons.forEach(person => {
        if (person && typeof person === 'string') {
          persons.add(person)
        }
      })
    }
  })
  return Array.from(persons).sort()
})

const allAuthors = computed(() => {
  const authors = new Set()
  props.articles.forEach(article => {
    if (article.publisher && typeof article.publisher === 'string') {
      authors.add(article.publisher)
    }
    if (article.author) {
      if (Array.isArray(article.author)) {
        article.author.forEach(a => authors.add(a))
      } else {
        authors.add(article.author)
      }
    }
  })
  return Array.from(authors).sort()
})

const allEventTypes = computed(() => {
  const types = new Set()
  props.articles.forEach(article => {
    if (article.event_type && typeof article.event_type === 'string') {
      types.add(article.event_type)
    }
  })
  return Array.from(types).sort()
})

const filteredKeywords = computed(() => {
  if (!keywordInput.value) return []
  const searchTerm = keywordInput.value.toLowerCase()
  return allKeywords.value
    .filter(kw => kw.keyword.toLowerCase().includes(searchTerm))
    .slice(0, 5)
})

const filteredPersons = computed(() => {
  if (!personInput.value) return []
  const searchTerm = personInput.value.toLowerCase()
  return allPersons.value
    .filter(person => person.toLowerCase().includes(searchTerm))
    .slice(0, 5)
})

const filteredAuthors = computed(() => {
  if (!authorInput.value) return []
  const searchTerm = authorInput.value.toLowerCase()
  return allAuthors.value
    .filter(author => author.toLowerCase().includes(searchTerm))
    .slice(0, 5)
})

const filteredEventTypes = computed(() => {
  if (!eventTypeInput.value) return []
  const searchTerm = eventTypeInput.value.toLowerCase()
  return allEventTypes.value
    .filter(type => type.toLowerCase().includes(searchTerm))
    .slice(0, 5)
})

const hasActiveFilters = computed(() => {
  return Object.entries(localFilters.value).some(([key, value]) => {
    if (key.startsWith('exclude')) return false
    if (key === 'sortBy') return false
    if (Array.isArray(value)) return value.length > 0
    return value !== '' && value !== null && value !== undefined
  })
})

const activeFilterTags = computed(() => {
  const tags = []
  const f = localFilters.value

  if (f.dateFrom) tags.push({ key: 'dateFrom', label: `От ${formatDate(f.dateFrom)}` })
  if (f.dateTo) tags.push({ key: 'dateTo', label: `До ${formatDate(f.dateTo)}` })
  
  if (f.keywords.length) {
    const exclude = f.excludeKeywords ? 'ИСКЛ: ' : ''
    tags.push({ key: 'keywords', label: `${exclude}Ключ. слова (${f.keywords.length})` })
  }
  
  if (f.persons.length) {
    const exclude = f.excludePersons ? 'ИСКЛ: ' : ''
    tags.push({ key: 'persons', label: `${exclude}Персоны (${f.persons.length})` })
  }
  
  if (f.authors.length) {
    const exclude = f.excludeAuthors ? 'ИСКЛ: ' : ''
    tags.push({ key: 'authors', label: `${exclude}Авторы (${f.authors.length})` })
  }
  
  if (f.titleContains) {
    tags.push({ key: 'titleContains', label: `Заголовок: "${truncate(f.titleContains, 15)}"` })
  }
  
  if (f.eventType.length) {
    const exclude = f.excludeEventTypes ? 'ИСКЛ: ' : ''
    tags.push({ key: 'eventType', label: `${exclude}Типы (${f.eventType.length})` })
  }
  
  if (f.sentiment) {
    const sent = sentimentOptions.find(s => s.value === f.sentiment)
    tags.push({ key: 'sentiment', label: `Тон: ${sent?.label}` })
  }

  return tags
})

const markAsChanged = () => {
  hasFilterChanges.value = true
}

const applyFilters = () => {
  emit('update:filters', { ...localFilters.value })
  hasFilterChanges.value = false
}

const resetAllFilters = () => {
  localFilters.value = {
    dateFrom: '',
    dateTo: '',
    keywords: [],
    persons: [],
    authors: [],
    titleContains: '',
    eventType: [],
    sentiment: '',
    sortBy: 'date',
    excludeKeywords: false,
    excludePersons: false,
    excludeAuthors: false,
    excludeEventTypes: false
  }
  keywordInput.value = ''
  personInput.value = ''
  authorInput.value = ''
  eventTypeInput.value = ''
  hasFilterChanges.value = false
  emit('reset')
}

const truncate = (text, maxLength) => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU')
}

const getSentimentIcon = (sentiment) => {
  const map = { positive: '😊', negative: '😠', neutral: '😐' }
  return map[sentiment] || '❓'
}

const addKeyword = () => {
  if (keywordInput.value.trim()) {
    localFilters.value.keywords.push({
      keyword: keywordInput.value.trim(),
      sentiment: 'neutral'
    })
    keywordInput.value = ''
    markAsChanged()
  }
}

const selectKeyword = (keyword) => {
  if (!localFilters.value.keywords.find(k => k.keyword === keyword.keyword)) {
    localFilters.value.keywords.push(keyword)
    keywordInput.value = ''
    markAsChanged()
  }
}

const removeKeyword = (keyword) => {
  const idx = typeof keyword === 'object' 
    ? localFilters.value.keywords.findIndex(k => k.keyword === keyword.keyword)
    : localFilters.value.keywords.findIndex(k => k === keyword)
  if (idx !== -1) {
    localFilters.value.keywords.splice(idx, 1)
    markAsChanged()
  }
}

const addPerson = () => {
  if (personInput.value.trim()) {
    localFilters.value.persons.push(personInput.value.trim())
    personInput.value = ''
    markAsChanged()
  }
}

const selectPerson = (person) => {
  if (!localFilters.value.persons.includes(person)) {
    localFilters.value.persons.push(person)
    personInput.value = ''
    markAsChanged()
  }
}

const removePerson = (person) => {
  const idx = localFilters.value.persons.indexOf(person)
  if (idx !== -1) {
    localFilters.value.persons.splice(idx, 1)
    markAsChanged()
  }
}

const addAuthor = () => {
  if (authorInput.value.trim()) {
    localFilters.value.authors.push(authorInput.value.trim())
    authorInput.value = ''
    markAsChanged()
  }
}

const selectAuthor = (author) => {
  if (!localFilters.value.authors.includes(author)) {
    localFilters.value.authors.push(author)
    authorInput.value = ''
    markAsChanged()
  }
}

const removeAuthor = (author) => {
  const idx = localFilters.value.authors.indexOf(author)
  if (idx !== -1) {
    localFilters.value.authors.splice(idx, 1)
    markAsChanged()
  }
}


const addEventType = () => {
  if (eventTypeInput.value.trim()) {
    localFilters.value.eventType.push(eventTypeInput.value.trim())
    eventTypeInput.value = ''
    markAsChanged()
  }
}

const selectEventType = (type) => {
  if (!localFilters.value.eventType.includes(type)) {
    localFilters.value.eventType.push(type)
    eventTypeInput.value = ''
    markAsChanged()
  }
}

const removeEventType = (type) => {
  const idx = localFilters.value.eventType.indexOf(type)
  if (idx !== -1) {
    localFilters.value.eventType.splice(idx, 1)
    markAsChanged()
  }
}

const toggleSentiment = (sentiment) => {
  localFilters.value.sentiment = localFilters.value.sentiment === sentiment ? '' : sentiment
  markAsChanged()
}

const removeFilter = (filterKey) => {
  if (['dateFrom', 'dateTo'].includes(filterKey)) {
    localFilters.value[filterKey] = ''
  } else if (['keywords', 'persons', 'authors', 'eventType'].includes(filterKey)) {
    localFilters.value[filterKey] = []
  } else if (filterKey === 'titleContains') {
    localFilters.value.titleContains = ''
  } else if (filterKey === 'sentiment') {
    localFilters.value.sentiment = ''
  }
  markAsChanged()
}

watch(() => props.filters, (newFilters) => {
  if (newFilters) {
    localFilters.value = { ...localFilters.value, ...newFilters }
    hasFilterChanges.value = false
  }
}, { immediate: true })

onMounted(() => {
  hasFilterChanges.value = false
})
</script>

<style scoped>
.filters-panel {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.1);
  height: calc(100vh - 100px);
  position: sticky;
  top: 20px;
  overflow-y: auto;
  overflow-x: hidden;
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.1);
}

.filters-header h3 {
  color: #2d3748;
  margin: 0;
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.apply-btn, .reset-btn {
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
  min-width: 100px;
  letter-spacing: 0.3px;
}

.apply-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.apply-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.apply-btn:disabled,
.apply-btn.disabled {
  background: #cbd5e0;
  cursor: not-allowed;
  opacity: 0.6;
  box-shadow: none;
  transform: none !important;
}

.reset-btn {
  background: white;
  color: #718096;
  border: 2px solid #e2e8f0;
}

.reset-btn:hover:not(:disabled) {
  background: #f7fafc;
  color: #4a5568;
  border-color: #cbd5e0;
  transform: translateY(-2px);
}

.reset-btn:disabled,
.reset-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.filters-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  color: #4a5568;
  font-size: 0.95rem;
}

.label-icon {
  font-size: 1.2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.date-filters {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.date-input-wrapper {
  position: relative;
}

.date-input {
  position: relative;
}

.date-input .input-label {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.8rem;
  color: #718096;
  background: white;
  padding: 0 4px;
  z-index: 1;
  pointer-events: none;
}

.date-input input {
  width: 100%;
  padding: 12px 12px 12px 35px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.95rem;
  transition: all 0.3s;
  background: white;
  color: #2d3748;
}

.date-input input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.filter-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.95rem;
  transition: all 0.3s;
  background: white;
  color: #2d3748;
}

.filter-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.filter-input::placeholder {
  color: #a0aec0;
}

.multi-select {
  position: relative;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.selected-tag {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 8px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.selected-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.selected-tag.person-tag {
  background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
}

.selected-tag.author-tag {
  background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
}

.selected-tag.event-tag {
  background: linear-gradient(135deg, #9f7aea 0%, #805ad5 100%);
}

.remove-tag {
  font-size: 1.1rem;
  font-weight: bold;
  opacity: 0.8;
  margin-left: 2px;
  transition: opacity 0.2s;
}

.remove-tag:hover {
  opacity: 1;
}

.suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
  margin-top: 4px;
}

.suggestion-item {
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 1px solid #f7fafc;
  font-size: 0.9rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.suggestion-item:hover {
  background: #f7fafc;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.sentiment-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  background: #f7fafc;
}

.exclude-filter {
  margin-top: 8px;
  padding: 12px;
  background: #fff5f5;
  border-radius: 10px;
  border-left: 4px solid #fc8181;
}

.exclude-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  color: #c53030;
  cursor: pointer;
}

.exclude-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #fc8181;
}

.exclude-text {
  cursor: pointer;
  font-weight: 500;
}

.sentiment-filters {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.sentiment-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
  min-height: 80px;
}

.sentiment-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

.sentiment-btn.active {
  border-width: 3px;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.sentiment-btn.positive.active {
  border-color: #48bb78;
  background: #f0fff4;
}

.sentiment-btn.negative.active {
  border-color: #f56565;
  background: #fff5f5;
}

.sentiment-btn.neutral.active {
  border-color: #a0aec0;
  background: #f7fafc;
}

.sentiment-icon {
  font-size: 1.8rem;
  margin-bottom: 8px;
}

.sentiment-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #4a5568;
}

.filter-select {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.95rem;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
  color: #4a5568;
  appearance: none;
  background-repeat: no-repeat;
  background-position: right 16px center;
  background-size: 16px;
}

.filter-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.active-filters {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 2px solid rgba(102, 126, 234, 0.1);
}

.active-filters h4 {
  color: #4a5568;
  margin-bottom: 12px;
  font-size: 0.95rem;
  font-weight: 600;
}

.active-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.active-tag {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 10px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.active-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
}
</style>