import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useDocumentStore } from './documentStore'

export const useFilterStore = defineStore('filter', () => {
  const documentStore = useDocumentStore()
  
  const filters = ref({
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

  const filteredArticles = computed(() => {
    if (!documentStore.articles.length) {
      return []
    }

    let articles = [...documentStore.articles]

    if (filters.value.dateFrom) {
      articles = articles.filter(article => {
        if (!article.date_parsed) return true
        try {
          const articleDate = new Date(article.date_parsed)
          const filterDate = new Date(filters.value.dateFrom)
          return articleDate >= filterDate
        } catch (e) {
          return true
        }
      })
    }

    if (filters.value.dateTo) {
      articles = articles.filter(article => {
        if (!article.date_parsed) return true
        try {
          const articleDate = new Date(article.date_parsed)
          const filterDate = new Date(filters.value.dateTo)
          return articleDate <= filterDate
        } catch (e) {
          return true
        }
      })
    }

    if (filters.value.keywords && filters.value.keywords.length > 0) {
      articles = articles.filter(article => {
        if (!article.keywords || !Array.isArray(article.keywords)) {
          return false
        }
        
        const filterKeywords = filters.value.keywords.map(kw => 
          typeof kw === 'object' ? kw.keyword.toLowerCase() : kw.toLowerCase()
        )
        
        const hasMatch = article.keywords.some(articleKw => {
          const articleKeyword = typeof articleKw === 'object' 
            ? (articleKw.keyword || articleKw.text || '').toLowerCase()
            : articleKw.toLowerCase()
          
          return filterKeywords.some(filterKw => 
            articleKeyword.includes(filterKw) || articleKeyword === filterKw
          )
        })
        
        if (filters.value.excludeKeywords) {
          return !hasMatch
        } else {
          return hasMatch
        }
      })
    }

    if (filters.value.persons && filters.value.persons.length > 0) {
      articles = articles.filter(article => {
        if (!article.persons || !Array.isArray(article.persons)) {
          return false
        }
        
        const articlePersons = article.persons.map(p => p.toLowerCase())
        const filterPersons = filters.value.persons.map(p => p.toLowerCase())
        
        const hasMatch = filterPersons.some(filterPerson =>
          articlePersons.some(articlePerson => 
            articlePerson.includes(filterPerson) ||
            articlePerson === filterPerson
          )
        )
        
        if (filters.value.excludePersons) {
          return !hasMatch
        } else {
          return hasMatch
        }
      })
    }

    if (filters.value.authors && filters.value.authors.length > 0) {
      articles = articles.filter(article => {
        const articleAuthors = []
        if (article.publisher) articleAuthors.push(article.publisher.toLowerCase())
        if (article.author) {
          if (Array.isArray(article.author)) {
            article.author.forEach(a => articleAuthors.push(a.toLowerCase()))
          } else {
            articleAuthors.push(article.author.toLowerCase())
          }
        }
        
        if (articleAuthors.length === 0) return false
        
        const filterAuthors = filters.value.authors.map(a => a.toLowerCase())
        const hasMatch = filterAuthors.some(filterAuthor =>
          articleAuthors.some(articleAuthor => 
            articleAuthor.includes(filterAuthor) ||
            articleAuthor === filterAuthor
          )
        )
        
        if (filters.value.excludeAuthors) {
          return !hasMatch
        } else {
          return hasMatch
        }
      })
    }

    if (filters.value.titleContains && filters.value.titleContains.trim()) {
      const search = filters.value.titleContains.toLowerCase().trim()
      articles = articles.filter(article => {
        if (!article.title) return false
        return article.title.toLowerCase().includes(search)
      })
    }

    if (filters.value.eventType && filters.value.eventType.length > 0) {
      articles = articles.filter(article => {
        const articleEventType = article.event_type || ''
        const filterEventTypes = filters.value.eventType
        
        const hasMatch = filterEventTypes.some(filterType =>
          articleEventType.toLowerCase() === filterType.toLowerCase() ||
          articleEventType.toLowerCase().includes(filterType.toLowerCase())
        )
        
        if (filters.value.excludeEventTypes) {
          return !hasMatch
        } else {
          return hasMatch
        }
      })
    }

    if (filters.value.sentiment) {
      articles = articles.filter(article => {
        if (!article.keywords) return false
        
        const hasSentiment = article.keywords.some(kw => {
          if (typeof kw === 'object') {
            return kw.sentiment === filters.value.sentiment
          }
          return false
        })
        
        if (article.sentiment) {
          return article.sentiment === filters.value.sentiment || hasSentiment
        }
        
        return hasSentiment
      })
    }

    articles.sort((a, b) => {
      switch (filters.value.sortBy) {
        case 'date':
          const dateA = a.date_parsed ? new Date(a.date_parsed).getTime() : 0
          const dateB = b.date_parsed ? new Date(b.date_parsed).getTime() : 0
          return dateB - dateA
          
        case 'title':
          return (a.title || '').localeCompare(b.title || '')
          
        case 'relevance':
          const getRelevanceScore = (article) => {
            if (!article.keywords || !Array.isArray(article.keywords)) return 0
            
            return article.keywords.reduce((sum, kw) => {
              let score = 0
              if (typeof kw === 'object') {
                score = kw.relevance_score || kw.score || kw.importance || 0
              }
              if (typeof kw === 'string') {
                score = 1
              }
              return sum + (typeof score === 'number' ? score : 0)
            }, 0)
          }
          
          const scoreA = getRelevanceScore(a)
          const scoreB = getRelevanceScore(b)
          return scoreB - scoreA
          
        case 'length':
          const lengthA = a.word_count || (a.text ? a.text.length : 0) || 0
          const lengthB = b.word_count || (b.text ? b.text.length : 0) || 0
          return lengthB - lengthA
          
        default:
          return 0
      }
    })

    return articles
  })

  const hasActiveFilters = computed(() => {
    return Object.entries(filters.value).some(([key, value]) => {
      if (key.startsWith('exclude')) return false
      if (key === 'sortBy') return false
      if (Array.isArray(value)) return value.length > 0
      return value !== '' && value !== null && value !== undefined
    })
  })

  const activeFilterTags = computed(() => {
    const tags = []
    const f = filters.value

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
      const sentimentOptions = [
        { value: 'positive', label: 'Положительная' },
        { value: 'negative', label: 'Отрицательная' },
        { value: 'neutral', label: 'Нейтральная' }
      ]
      const sent = sentimentOptions.find(s => s.value === f.sentiment)
      tags.push({ key: 'sentiment', label: `Тон: ${sent?.label}` })
    }

    return tags
  })

  const updateFilters = (newFilters) => {
    Object.keys(newFilters).forEach(key => {
      if (Array.isArray(newFilters[key])) {
        filters.value[key] = newFilters[key]
      } else if (key in filters.value) {
        filters.value[key] = newFilters[key]
      }
    })
  }

  const resetFilters = () => {
    filters.value = {
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
  }

  const removeFilter = (filterKey) => {
    if (['dateFrom', 'dateTo'].includes(filterKey)) {
      filters.value[filterKey] = ''
    } else if (['keywords', 'persons', 'authors', 'eventType'].includes(filterKey)) {
      filters.value[filterKey] = []
    } else if (filterKey === 'titleContains') {
      filters.value.titleContains = ''
    } else if (filterKey === 'sentiment') {
      filters.value.sentiment = ''
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleDateString('ru-RU')
  }

  const truncate = (text, maxLength) => {
    if (!text) return ''
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
  }

  return {
    filters,
    
    filteredArticles,
    hasActiveFilters,
    activeFilterTags,
    
    updateFilters,
    resetFilters,
    removeFilter
  }
})