<template>
  <button @click="openDashboard" class="dashboard-btn">
    📊 Сформировать дашборд
  </button>
  <div class="dashboard">
    <div class="header">
      <h1>📄 Анализатор документов</h1>
      <p>Загрузите текстовый документ для автоматического анализа</p>
    </div>

    <div class="main-content">
      <div class="left-panel">
        <FileUpload 
          @file-selected="handleFileSelected" 
          @upload="handleFileUpload"
          :loading="documentStore.loading"
        />
        
        <FiltersPanel 
          v-if="documentStore.hasResults"
          :filters="filterStore.filters"
          :articles="documentStore.articles"
          @update:filters="handleFilterChange"
          @reset="resetFilters"
        />
      </div>

      <div class="right-panel">
        <AnalysisResults 
          v-if="documentStore.hasResults"
          :articles="filterStore.filteredArticles"
          :total-articles="documentStore.articlesCount"
          :loading="documentStore.loading"
          @article-click="handleArticleClick"
        />
        
        <div v-else-if="documentStore.loading" class="loading-state">
          <div class="spinner"></div>
          <p>Анализируем документ...</p>
          <p class="progress">{{ documentStore.progress }}</p>
        </div>

        <div v-else class="welcome-state">
          <div class="welcome-icon">📊</div>
          <h2>Начните анализ документа</h2>
          <p>Загрузите .txt файл с текстом для анализа</p>
          <ul class="features">
            <li>📝 Автоматическое выделение статей</li>
            <li>👤 Извлечение имен и персоналий</li>
            <li>🔑 Поиск ключевых слов</li>
            <li>📅 Определение дат событий</li>
            <li>📊 Классификация типов событий</li>
          </ul>
        </div>
      </div>
    </div>

    <DocumentViewer 
      v-if="documentStore.selectedArticle"
      :article="documentStore.selectedArticle"
      @close="documentStore.clearSelectedArticle"
    />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { onMounted } from 'vue'
import FileUpload from '../components/FileUpload.vue'
import AnalysisResults from '../components/AnalysisResults.vue'
import FiltersPanel from '../components/FiltersPanel.vue'
import DocumentViewer from '../components/DocumentViewer.vue'
import { useDocumentStore } from '../stores/documentStore'
import { useFilterStore } from '../stores/filterStore'

const documentStore = useDocumentStore()
const filterStore = useFilterStore()
const router = useRouter()

const openDashboard = () => {
  router.push('/dashboard')
}

const handleFileSelected = (selectedFile) => {
  documentStore.setFile(selectedFile)
  console.log('Файл выбран:', selectedFile.name)
}

const handleFileUpload = async () => {
  if (!documentStore.file) {
    alert('Пожалуйста, выберите файл')
    return
  }

  const formData = new FormData()
  formData.append('file', documentStore.file)
  
  const progressInterval = setInterval(() => {
    if (documentStore.progress === 'Анализ завершен!') {
      clearInterval(progressInterval)
    } else if (documentStore.progress.includes('95%')) {
      documentStore.updateProgress('Анализ завершен!')
    } else {
      const current = parseInt(documentStore.progress) || 0
      documentStore.updateProgress(`${Math.min(current + 5, 95)}%`)
    }
  }, 200)

  try {
    await documentStore.analyze(formData)
    clearInterval(progressInterval)
    documentStore.updateProgress('')
    console.log('Анализ завершен:', documentStore.results)
    
  } catch (error) {
    console.error('Ошибка анализа:', error)
    alert(`Ошибка: ${error.message}`)
    clearInterval(progressInterval)
    documentStore.updateProgress('')
  }
}

const handleArticleClick = (article) => {
  documentStore.setSelectedArticle(article)
  console.log('Выбрана статья:', article.title)
}

const handleFilterChange = (newFilters) => {
  filterStore.updateFilters(newFilters)
}

const resetFilters = () => {
  filterStore.resetFilters()
}

onMounted(() => {
  console.log('Dashboard mounted')
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 40px;
  color: white;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.header p {
  font-size: 1.1rem;
  opacity: 0.9;
}

.main-content {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 30px;
  max-width: 1400px;
  margin: 0 auto;
}

.left-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.right-panel {
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
  min-height: 500px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #666;
}

.spinner {
  border: 5px solid #f3f3f3;
  border-top: 5px solid #667eea;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.progress {
  margin-top: 15px;
  font-weight: 600;
  color: #667eea;
}

.welcome-state {
  text-align: center;
  padding: 60px 20px;
}

.welcome-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

.welcome-state h2 {
  color: #333;
  margin-bottom: 15px;
}

.welcome-state p {
  color: #666;
  margin-bottom: 30px;
  font-size: 1.1rem;
}

.features {
  list-style: none;
  text-align: left;
  max-width: 400px;
  margin: 30px auto 0;
}

.features li {
  padding: 10px 0;
  color: #555;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  gap: 10px;
}

.features li:last-child {
  border-bottom: none;
}


</style>