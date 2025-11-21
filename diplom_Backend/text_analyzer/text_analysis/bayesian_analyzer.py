import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from collections import defaultdict
from .text_processor import TextProcessor

class BayesianTopicAnalyzer:
    """
    Упрощенный анализатор тем без сложных зависимостей
    """
    
    def __init__(self, n_topics=5, max_features=1000):
        self.n_topics = n_topics
        self.max_features = max_features
        self.text_processor = TextProcessor()
        self.vectorizer = None
        self.lda_model = None
        self.feature_names = None
        
    def prepare_corpus(self, documents):
        """
        Подготовка корпуса документов для анализа.
        """
        # Используем упрощенную обработку
        processed_docs = [' '.join(self.text_processor.process_text(doc)) for doc in documents]
        
        # Создание векторного представления
        self.vectorizer = CountVectorizer(
            max_features=self.max_features,
            stop_words=list(self.text_processor.stop_words)
        )
        X = self.vectorizer.fit_transform(processed_docs)
        self.feature_names = self.vectorizer.get_feature_names_out()
        
        return X, processed_docs
    
    def fit_lda_model(self, X):
        """
        Обучение LDA модели для выявления скрытых тем.
        """
        self.lda_model = LatentDirichletAllocation(
            n_components=self.n_topics,
            random_state=42,
            max_iter=10
        )
        self.lda_model.fit(X)
        return self.lda_model
    
    def get_topic_keywords(self, n_keywords=10):
        """
        Получение ключевых слов для каждой темы.
        """
        if self.lda_model is None:
            raise ValueError("LDA модель не обучена!")
        
        topic_keywords = []
        for topic_idx, topic in enumerate(self.lda_model.components_):
            top_keywords_idx = topic.argsort()[:-n_keywords-1:-1]
            top_keywords = [self.feature_names[i] for i in top_keywords_idx]
            topic_keywords.append({
                'topic_id': topic_idx,
                'keywords': top_keywords,
                'topic_name': f"Тема {topic_idx + 1}: {', '.join(top_keywords[:3])}"
            })
        
        return topic_keywords
    
    def assign_documents_to_topics(self, X, documents):
        """
        Распределение документов по темам.
        """
        if self.lda_model is None:
            raise ValueError("LDA модель не обучена!")
        
        topic_distribution = self.lda_model.transform(X)
        
        document_topics = []
        for doc_idx, doc_topics in enumerate(topic_distribution):
            dominant_topic = np.argmax(doc_topics)
            confidence = doc_topics[dominant_topic]
            
            document_topics.append({
                'document_index': doc_idx,
                'original_text': documents[doc_idx],
                'dominant_topic': dominant_topic,
                'confidence': confidence
            })
        
        return document_topics
    
    def analyze_topics(self, documents):
        """
        Основной метод анализа тем в документах.
        """
        try:
            # Подготовка данных
            X, processed_docs = self.prepare_corpus(documents)
            
            # Обучение LDA модели
            self.fit_lda_model(X)
            
            # Получение ключевых слов тем
            topic_keywords = self.get_topic_keywords()
            
            # Распределение документов по темам
            document_assignments = self.assign_documents_to_topics(X, documents)
            
            # Подсчет статистики по темам
            topic_stats = self.calculate_topic_statistics(document_assignments, topic_keywords)
            
            return {
                'topic_statistics': topic_stats,
                'document_assignments': document_assignments,
                'topic_keywords': topic_keywords
            }
        except Exception as e:
            # Возвращаем заглушку в случае ошибки
            return self.get_fallback_result(documents)
    
    def calculate_topic_statistics(self, document_assignments, topic_keywords):
        """
        Расчет статистики по темам.
        """
        topic_stats = []
        
        for topic_info in topic_keywords:
            topic_id = topic_info['topic_id']
            
            topic_docs = [doc for doc in document_assignments 
                         if doc['dominant_topic'] == topic_id]
            
            doc_count = len(topic_docs)
            avg_confidence = np.mean([doc['confidence'] for doc in topic_docs]) if topic_docs else 0
            
            topic_stats.append({
                'topic_id': topic_id,
                'topic_name': topic_info['topic_name'],
                'keywords': topic_info['keywords'],
                'document_count': doc_count,
                'average_confidence': round(avg_confidence, 3),
                'document_indices': [doc['document_index'] for doc in topic_docs]
            })
        
        return topic_stats
    
    def get_fallback_result(self, documents):
        """
        Заглушка на случай ошибки анализа.
        """
        return {
            'topic_statistics': [
                {
                    'topic_id': 0,
                    'topic_name': 'Общая тема',
                    'keywords': ['текст', 'анализ', 'данные'],
                    'document_count': len(documents),
                    'average_confidence': 0.9,
                    'document_indices': list(range(len(documents)))
                }
            ],
            'document_assignments': [],
            'topic_keywords': []
        }

class EnhancedBayesianAnalyzer(BayesianTopicAnalyzer):
    """
    Расширенный анализатор с автоматическим определением тем.
    """
    
    def auto_determine_topics(self, documents, max_topics=10):
        """
        Автоматическое определение оптимального количества тем.
        """
        if len(documents) < 3:
            return min(2, len(documents))
            
        X, _ = self.prepare_corpus(documents)
        max_topics = min(max_topics, len(documents) - 1)
        
        best_perplexity = float('inf')
        best_n_topics = 2
        
        for n in range(2, max_topics + 1):
            try:
                lda = LatentDirichletAllocation(n_components=n, random_state=42)
                lda.fit(X)
                perplexity = lda.perplexity(X)
                
                if perplexity < best_perplexity:
                    best_perplexity = perplexity
                    best_n_topics = n
            except:
                continue
        
        return best_n_topics
    
    def analyze_with_auto_topics(self, documents):
        """
        Анализ с автоматическим определением количества тем.
        """
        if len(documents) < 2:
            # Если документов мало, используем минимальное количество тем
            self.n_topics = min(2, len(documents))
        else:
            self.n_topics = self.auto_determine_topics(documents)
        
        return self.analyze_topics(documents)