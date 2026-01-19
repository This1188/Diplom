<template>
  <div class="document-viewer-overlay" @click.self="close">
    <div class="document-viewer">
      <div class="viewer-header">
        <h2>{{ article.title }}</h2>
        <button @click="close" class="close-btn">✕</button>
      </div>
      
      <div class="viewer-content">
        <div class="article-meta">
          <div class="meta-item" v-if="article.date">
            <span class="meta-label">📅 Дата:</span>
            <span class="meta-value">{{ formatDate(article.date) }}</span>
          </div>
          <div class="meta-item" v-if="article.event_type">
            <span class="meta-label">📊 Тип события:</span>
            <span class="meta-value">{{ article.event_type }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">📝 Длина:</span>
            <span class="meta-value">{{ article.word_count }} слов, {{ article.char_count }} симв.</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Публикация:</span>
            <span class="meta-value">{{ article.publisher }}</span>
          </div>
        </div>

        <div class="article-content">
          <h3>Полный текст:</h3>
          <div class="content-text">
            {{ article.raw_text || article.content }}
          </div>
        </div>

        <div class="analysis-results">
          <div class="result-section" v-if="article.persons && article.persons.length">
            <h3>👤 Персоны:</h3>
            <div class="tags">
              <span v-for="person in article.persons" :key="person" class="tag person">
                {{ person }}
              </span>
            </div>
          </div>

          <div class="result-section" v-if="article.keywords && article.keywords.length">
            <h3>🏷️ Ключевые слова:</h3>
            <div class="tags">
              <span 
                v-for="keyword in article.keywords" 
                :key="keyword.keyword"
                class="tag keyword"
                :class="`sentiment-${keyword.sentiment}`"
              >
                {{ keyword.keyword }}
                <span class="sentiment-badge" :class="keyword.sentiment">
                  {{ getSentimentEmoji(keyword.sentiment) }}
                </span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="viewer-footer">
        <button @click="close" class="btn-secondary">Закрыть</button>
        <button @click="copyToClipboard" class="btn-primary">
          📋 Копировать текст
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  article: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}

const formatDate = (dateString) => {
  if (!dateString || dateString === 'Дата не найдена') {
    return 'Не указана'
  }
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

const getSentimentEmoji = (sentiment) => {
  const emojis = {
    'positive': '😊',
    'negative': '😠',
    'neutral': '😐'
  }
  return emojis[sentiment] || '❓'
}

const copyToClipboard = async () => {
  try {
    const text = props.article.raw_text || props.article.content
    await navigator.clipboard.writeText(text)
    alert('Текст скопирован в буфер обмена')
  } catch (err) {
    console.error('Ошибка копирования:', err)
    alert('Не удалось скопировать текст')
  }
}
</script>

<style scoped>
.document-viewer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.document-viewer {
  background: white;
  border-radius: 15px;
  width: 90%;
  max-width: 1000px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 30px;
  border-bottom: 2px solid #f0f0f0;
}

.viewer-header h2 {
  color: #333;
  margin: 0;
  font-size: 1.5rem;
  flex: 1;
  padding-right: 20px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.8rem;
  color: #666;
  cursor: pointer;
  padding: 5px;
  border-radius: 5px;
  transition: all 0.3s;
}

.close-btn:hover {
  color: #333;
  background: #f5f5f5;
}

.viewer-content {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 30px;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 10px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.meta-label {
  font-weight: 600;
  color: #555;
}

.meta-value {
  color: #333;
}

.article-content {
  margin-bottom: 30px;
}

.article-content h3 {
  color: #444;
  margin-bottom: 15px;
  font-size: 1.2rem;
}

.content-text {
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
  background: #f9f9f9;
  padding: 20px;
  border-radius: 10px;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #eee;
}

.analysis-results {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.result-section h3 {
  color: #444;
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.tag.person {
  background: #e3f2fd;
  color: #1976d2;
  border: 1px solid #bbdefb;
}

.tag.keyword {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid;
}

.tag.keyword.sentiment-positive {
  background: #e8f5e9;
  color: #2e7d32;
  border-color: #c8e6c9;
}

.tag.keyword.sentiment-negative {
  background: #ffebee;
  color: #c62828;
  border-color: #ffcdd2;
}

.tag.keyword.sentiment-neutral {
  background: #f5f5f5;
  color: #616161;
  border-color: #e0e0e0;
}

.sentiment-badge {
  padding: 2px 6px;
  border-radius: 50%;
  font-size: 0.8rem;
}

.viewer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  padding: 20px 30px;
  border-top: 2px solid #f0f0f0;
  background: #f9f9f9;
  border-radius: 0 0 15px 15px;
}

.btn-primary, .btn-secondary {
  padding: 12px 25px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #f5f5f5;
  color: #666;
}

.btn-secondary:hover {
  background: #e0e0e0;
  color: #333;
}

</style>