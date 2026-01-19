<template>
  <div class="analysis-results">
    <div class="results-header">
      <div class="header-left">
        <h2>Результаты анализа</h2>
        <div class="stats">
          <span class="stat-item">
            📊 <strong>{{ articles.length }}</strong> из {{ totalArticles }} статей
          </span>
          <span v-if="selectedKeywords" class="stat-item">
            🔍 {{ selectedKeywords }} ключевых слов
          </span>
          <span v-if="selectedPersons" class="stat-item">
            👥 {{ selectedPersons }} персон
          </span>
        </div>
      </div>
      
      <div class="header-right">
        <div class="view-controls">
          <button 
            @click="viewMode = 'list'"
            :class="{ active: viewMode === 'list' }"
            title="Список"
          >
            📃
          </button>
          <button 
            @click="viewMode = 'grid'"
            :class="{ active: viewMode === 'grid' }"
            title="Сетка"
          >
            🏞️
          </button>
        </div>
        
        <button 
          v-if="articles.length > 0"
          @click="exportResults"
          class="export-btn"
          title="Экспорт результатов"
        >
          📥 Экспорт
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-placeholder">
      <div class="spinner-small"></div>
      <p>Загрузка результатов...</p>
    </div>

    <div v-else-if="articles.length === 0" class="empty-state">
      <div class="empty-icon">🔍</div>
      <h3>Статьи не найдены</h3>
      <p>Попробуйте изменить параметры фильтрации</p>
    </div>

    <div v-else :class="['articles-container', viewMode]">
      <div 
        v-for="(article, index) in articles" 
        :key="article.id || index"
        class="article-card"
        @click="$emit('article-click', article)"
      >
        <div class="article-header">
          <div class="article-meta">
            <span class="article-index">#{{ index + 1 }}</span>
            <span v-if="article.date" class="article-date">
              📅 {{ formatDate(article.date) }}
            </span>
          </div>
          <h3 class="article-title" :title="article.title">
            {{ truncateText(article.title, 80) }}
          </h3>
        </div>

        <div class="article-preview">
          {{ truncateText(article.content || article.preview, 150) }}
        </div>

        <div class="article-tags">
          <div v-if="article.persons?.length" class="tag-section">
            <span class="tag-label">👤 Персоны:</span>
            <div class="tags">
              <span 
                v-for="person in article.persons.slice(0, 3)" 
                :key="person"
                class="tag person-tag"
              >
                {{ person }}
              </span>
              <span v-if="article.persons.length > 3" class="tag-more">
                +{{ article.persons.length - 3 }}
              </span>
            </div>
          </div>

          <div v-if="article.keywords?.length" class="tag-section">
            <span class="tag-label">🏷️ Ключевые слова:</span>
            <div class="tags">
              <span 
                v-for="keyword in article.keywords.slice(0, 3)" 
                :key="keyword.keyword"
                class="tag keyword-tag"
                :class="`sentiment-${keyword.sentiment}`"
                :title="`Тональность: ${getSentimentText(keyword.sentiment)}`"
              >
                {{ keyword.keyword }}
                <span class="sentiment-dot" :class="keyword.sentiment"></span>
              </span>
              <span v-if="article.keywords.length > 3" class="tag-more">
                +{{ article.keywords.length - 3 }}
              </span>
            </div>
          </div>

          <div v-if="article.event_type" class="tag-section">
            <span class="tag-label">📊 Тип события:</span>
            <span class="event-type-tag">
              {{ article.event_type }}
            </span>
          </div>
        </div>

        <div class="article-footer">
          <div class="article-stats">
            <span class="stat" title="Количество слов">
              📝 {{ article.word_count || '?' }} слов
            </span>
            <span class="stat" title="Количество символов">
              🔤 {{ article.char_count || '?' }} симв.
            </span>
          </div>
          <button class="view-btn">
            Подробнее →
          </button>
        </div>
      </div>
    </div>

    <div v-if="articles.length > 0" class="pagination">
      <button 
        @click="loadMore"
        class="load-more-btn"
        v-if="articles.length < totalArticles"
      >
        📥 Загрузить еще
      </button>
      <div class="pagination-info">
        Показано {{ articles.length }} из {{ totalArticles }} статей
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  articles: {
    type: Array,
    required: true,
    default: () => []
  },
  totalArticles: {
    type: Number,
    required: true,
    default: 0
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['article-click'])

const viewMode = ref('list')
const displayedCount = ref(10)

const selectedKeywords = computed(() => {
  if (!props.articles.length) return 0
  return props.articles.reduce((total, article) => {
    return total + (article.keywords?.length || 0)
  }, 0)
})

const selectedPersons = computed(() => {
  if (!props.articles.length) return 0
  return props.articles.reduce((total, article) => {
    return total + (article.persons?.length || 0)
  }, 0)
})

const truncateText = (text, maxLength) => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const formatDate = (dateString) => {
  if (!dateString || dateString === 'Дата не найдена') return 'Дата не указана'
  
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return dateString
    
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    })
  } catch {
    return dateString
  }
}

const getSentimentText = (sentiment) => {
  const map = {
    'positive': 'Положительная',
    'negative': 'Отрицательная',
    'neutral': 'Нейтральная'
  }
  return map[sentiment] || sentiment
}

const loadMore = () => {
  displayedCount.value += 10
}

const exportResults = () => {
  const dataStr = JSON.stringify(props.articles, null, 2)
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
  
  const exportFileDefaultName = `анализ_документа_${new Date().toISOString().split('T')[0]}.json`
  
  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', exportFileDefaultName)
  linkElement.click()
  
  alert('Результаты экспортированы в JSON файл')
}
</script>

<style scoped>
.analysis-results {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.header-left h2 {
  color: #333;
  margin-bottom: 10px;
  font-size: 1.8rem;
}

.stats {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.stat-item {
  background: #f8f9fa;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.9rem;
  color: #666;
  display: flex;
  align-items: center;
  gap: 5px;
}

.stat-item strong {
  color: #667eea;
  margin: 0 3px;
}

.header-right {
  display: flex;
  gap: 15px;
  align-items: center;
}

.view-controls {
  display: flex;
  gap: 5px;
  background: #f5f5f5;
  padding: 4px;
  border-radius: 8px;
}

.view-controls button {
  background: none;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.3s;
}

.view-controls button.active {
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.export-btn {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s;
}

.export-btn:hover {
  background: #45a049;
  transform: translateY(-1px);
}

.loading-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #666;
}

.spinner-small {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #888;
}

.empty-icon {
  font-size: 60px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state h3 {
  margin-bottom: 10px;
  color: #666;
}

.articles-container {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px;
}

.articles-container.list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.articles-container.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  gap: 20px;
}

.article-card {
  background: white;
  border: 1px solid #eaeaea;
  border-radius: 12px;
  padding: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.article-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  border-color: #667eea;
}

.article-header {
  margin-bottom: 15px;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.article-index {
  background: #667eea;
  color: white;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.article-date {
  color: #666;
  font-size: 0.85rem;
  background: #f5f5f5;
  padding: 3px 10px;
  border-radius: 4px;
}

.article-title {
  color: #333;
  font-size: 1.3rem;
  line-height: 1.4;
  margin: 0;
  font-weight: 600;
}

.article-preview {
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
  flex: 1;
  font-size: 0.95rem;
}

.article-tags {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.tag-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tag-label {
  font-size: 0.85rem;
  color: #888;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 5px;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.person-tag {
  background: #e3f2fd;
  color: #1976d2;
  border: 1px solid #bbdefb;
}

.keyword-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  border: 1px solid;
}

.keyword-tag.sentiment-positive {
  background: #e8f5e9;
  color: #2e7d32;
  border-color: #c8e6c9;
}

.keyword-tag.sentiment-negative {
  background: #ffebee;
  color: #c62828;
  border-color: #ffcdd2;
}

.keyword-tag.sentiment-neutral {
  background: #f5f5f5;
  color: #616161;
  border-color: #e0e0e0;
}

.sentiment-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.sentiment-dot.positive {
  background: #4CAF50;
}

.sentiment-dot.negative {
  background: #f44336;
}

.sentiment-dot.neutral {
  background: #9e9e9e;
}

.event-type-tag {
  background: #f3e5f5;
  color: #7b1fa2;
  padding: 5px 15px;
  border-radius: 6px;
  font-size: 0.9rem;
  display: inline-block;
  border: 1px solid #e1bee7;
}

.tag-more {
  color: #888;
  font-size: 0.85rem;
  align-self: center;
}

.article-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.article-stats {
  display: flex;
  gap: 15px;
}

.article-stats .stat {
  font-size: 0.85rem;
  color: #888;
  display: flex;
  align-items: center;
  gap: 5px;
}

.view-btn {
  background: transparent;
  color: #667eea;
  border: 1px solid #667eea;
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.view-btn:hover {
  background: #667eea;
  color: white;
}

.pagination {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 2px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.load-more-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.load-more-btn:hover {
  background: #5a67d8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.pagination-info {
  color: #888;
  font-size: 0.9rem;
}
</style>