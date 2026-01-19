import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { analyzeDocument } from '../services/api'

export const useDocumentStore = defineStore('document', () => {
  const file = ref(null)
  const results = ref(null)
  const loading = ref(false)
  const progress = ref('')
  const selectedArticle = ref(null)
  const error = ref(null)

  const articlesCount = computed(() => results.value?.articles_count || 0)
  const articles = computed(() => results.value?.articles || [])
  const hasResults = computed(() => results.value !== null)
  const uniqueValues = computed(() => {
    const values = {
      keywords: new Set(),
      persons: new Set(),
      titles: new Set(),
      eventTypes: new Set(),
      authors: new Set()
    }
    
    if (!articles.value.length) return values
    
    articles.value.forEach(article => {
      if (article.keywords && Array.isArray(article.keywords)) {
        article.keywords.forEach(kw => {
          if (typeof kw === 'string') {
            values.keywords.add(kw)
          } else if (kw && kw.keyword) {
            values.keywords.add(kw.keyword)
          }
        })
      }
      
      if (article.persons && Array.isArray(article.persons)) {
        article.persons.forEach(person => {
          if (person && typeof person === 'string') {
            values.persons.add(person)
          }
        })
      }
      
      if (article.publisher && typeof article.publisher === 'string') {
        values.authors.add(article.publisher)
      }
      
      if (article.author) {
        if (Array.isArray(article.author)) {
          article.author.forEach(a => values.authors.add(a))
        } else {
          values.authors.add(article.author)
        }
      }
      
      if (article.event_type && typeof article.event_type === 'string') {
        values.eventTypes.add(article.event_type)
      }
    })
    
    return {
      keywords: Array.from(values.keywords).sort(),
      persons: Array.from(values.persons).sort(),
      authors: Array.from(values.authors).sort(),
      eventTypes: Array.from(values.eventTypes).sort()
    }
  })

  const setFile = (selectedFile) => {
    file.value = selectedFile
  }

  const clearFile = () => {
    file.value = null
  }

  const setSelectedArticle = (article) => {
    selectedArticle.value = article
  }

  const clearSelectedArticle = () => {
    selectedArticle.value = null
  }

  const analyze = async (formData) => {
    loading.value = true
    error.value = null
    progress.value = '0%'
    
    try {
      const response = await analyzeDocument(formData)
      results.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || err.message
      throw err
    } finally {
      loading.value = false
      progress.value = ''
    }
  }

  const clearResults = () => {
    results.value = null
    error.value = null
  }

  const updateProgress = (value) => {
    progress.value = value
  }

  return {
    file,
    results,
    loading,
    progress,
    selectedArticle,
    error,
    
    articlesCount,
    articles,
    hasResults,
    uniqueValues,
    
    setFile,
    clearFile,
    setSelectedArticle,
    clearSelectedArticle,
    analyze,
    clearResults,
    updateProgress
  }
})