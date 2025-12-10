import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from collections import defaultdict
from .text_processor import TextProcessor

class BayesianTopicAnalyzer:
    """
    Улучшенный анализатор тем с настройками для различных тематик
    """
    
    def __init__(self, n_topics=5, max_features=2000, use_tfidf=True):
        self.n_topics = n_topics
        self.max_features = max_features
        self.use_tfidf = use_tfidf
        self.text_processor = TextProcessor()
        self.vectorizer = None
        self.lda_model = None
        self.feature_names = None
        
    def prepare_corpus(self, documents):
        """
        Подготовка корпуса документов для анализа.
        """
        # Улучшенная обработка текста
        processed_docs = []
        for doc in documents:
            tokens = self.text_processor.process_text(doc)
            # Сохраняем именованные сущности и специфические термины
            processed_doc = ' '.join(tokens)
            processed_docs.append(processed_doc)
        
        # Выбираем векторный метод
        if self.use_tfidf:
            self.vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                min_df=2,  # Минимальная частота слова
                max_df=0.95,  # Максимальная частота слова (убираем слишком частые)
                stop_words=list(self.text_processor.stop_words),
                ngram_range=(1, 3)  # Учитываем словосочетания до 3 слов
            )
        else:
            self.vectorizer = CountVectorizer(
                max_features=self.max_features,
                min_df=2,
                max_df=0.95,
                stop_words=list(self.text_processor.stop_words),
                ngram_range=(1, 2)
            )
        
        X = self.vectorizer.fit_transform(processed_docs)
        self.feature_names = self.vectorizer.get_feature_names_out()
        
        print(f"Словарь размером: {len(self.feature_names)} слов")
        print(f"Матрица документов: {X.shape[0]} документов x {X.shape[1]} признаков")
        
        return X, processed_docs
    
    def fit_lda_model(self, X):
        """
        Обучение LDA модели для выявления скрытых тем.
        """
        # Адаптируем количество тем под размер данных
        actual_topics = min(self.n_topics, X.shape[0] - 1)
        if actual_topics < 2:
            actual_topics = 2
        
        print(f"Обучение LDA с {actual_topics} темами...")
        
        self.lda_model = LatentDirichletAllocation(
            n_components=actual_topics,
            random_state=42,
            max_iter=50,  # Увеличили итерации
            learning_method='online',
            learning_offset=50.,
            batch_size=128,
            evaluate_every=5,
            perp_tol=0.01
        )
        self.lda_model.fit(X)
        
        # Выводим перплексию для оценки качества
        perplexity = self.lda_model.perplexity(X)
        print(f"Перплексия модели: {perplexity:.2f}")
        
        return self.lda_model
    
    def get_topic_keywords(self, n_keywords=15):
        """
        Получение ключевых слов для каждой темы.
        """
        if self.lda_model is None:
            raise ValueError("LDA модель не обучена!")
        
        topic_keywords = []
        for topic_idx, topic in enumerate(self.lda_model.components_):
            # Получаем топ ключевых слов
            top_keywords_idx = topic.argsort()[:-n_keywords-1:-1]
            top_keywords = [self.feature_names[i] for i in top_keywords_idx]
            
            # Генерируем осмысленное название темы
            if len(top_keywords) >= 3:
                # Берем наиболее репрезентативные слова (не слишком частые и не слишком редкие)
                mid_idx = len(top_keywords) // 2
                topic_name_words = [top_keywords[0], top_keywords[mid_idx], top_keywords[-1]]
                topic_name = f"Тема {topic_idx + 1}: {', '.join(topic_name_words[:3])}"
            else:
                topic_name = f"Тема {topic_idx + 1}: {', '.join(top_keywords[:3])}"
            
            topic_keywords.append({
                'topic_id': topic_idx,
                'keywords': top_keywords,
                'topic_name': topic_name
            })
        
        return topic_keywords
    
    def assign_documents_to_topics(self, X, documents, threshold=0.2):
        """
        Распределение документов по темам с порогом уверенности.
        """
        if self.lda_model is None:
            raise ValueError("LDA модель не обучена!")
        
        topic_distribution = self.lda_model.transform(X)
        
        document_topics = []
        for doc_idx, doc_topics in enumerate(topic_distribution):
            dominant_topic = np.argmax(doc_topics)
            confidence = doc_topics[dominant_topic]
            
            # Если уверенность низкая, помечаем как смешанную тему
            if confidence < threshold:
                dominant_topic = -1  # Смешанная/неопределенная тема
            
            document_topics.append({
                'document_index': doc_idx,
                'original_text': documents[doc_idx],
                'dominant_topic': dominant_topic,
                'confidence': confidence,
                'topic_distribution': doc_topics.tolist()
            })
        
        return document_topics
    
    def analyze_topics(self, documents):
        """
        Основной метод анализа тем в документах.
        """
        try:
            print(f"Начало анализа {len(documents)} документов...")
            
            # Подготовка данных
            X, processed_docs = self.prepare_corpus(documents)
            
            # Проверяем, достаточно ли разнообразия в данных
            unique_words = len(set(' '.join(processed_docs).split()))
            print(f"Уникальных слов: {unique_words}")
            
            if unique_words < 50:
                print("Мало уникальных слов, возможно, все документы на одну тему")
            
            # Обучение LDA модели
            self.fit_lda_model(X)
            
            # Получение ключевых слов тем
            topic_keywords = self.get_topic_keywords()
            
            # Распределение документов по темам
            document_assignments = self.assign_documents_to_topics(X, documents)
            
            # Подсчет статистики по темам
            topic_stats = self.calculate_topic_statistics(document_assignments, topic_keywords)
            
            # Выводим диагностическую информацию
            self.print_diagnostic_info(topic_stats, documents)
            
            return {
                'topic_statistics': topic_stats,
                'document_assignments': document_assignments,
                'topic_keywords': topic_keywords
            }
        except Exception as e:
            print(f"Ошибка анализа: {str(e)}")
            import traceback
            traceback.print_exc()
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
            if doc_count > 0:
                avg_confidence = np.mean([doc['confidence'] for doc in topic_docs])
            else:
                avg_confidence = 0
            
            topic_stats.append({
                'topic_id': topic_id,
                'topic_name': topic_info['topic_name'],
                'keywords': topic_info['keywords'],
                'document_count': doc_count,
                'average_confidence': round(avg_confidence, 3),
                'document_indices': [doc['document_index'] for doc in topic_docs]
            })
        
        # Добавляем смешанные/неопределенные темы
        mixed_docs = [doc for doc in document_assignments if doc['dominant_topic'] == -1]
        if mixed_docs:
            topic_stats.append({
                'topic_id': -1,
                'topic_name': 'Смешанная/Неопределенная тема',
                'keywords': ['разные', 'смешанные', 'темы'],
                'document_count': len(mixed_docs),
                'average_confidence': 0.1,
                'document_indices': [doc['document_index'] for doc in mixed_docs]
            })
        
        # Сортируем по количеству документов
        topic_stats.sort(key=lambda x: x['document_count'], reverse=True)
        
        return topic_stats
    
    def print_diagnostic_info(self, topic_stats, documents):
        """
        Вывод диагностической информации для отладки.
        """
        print("\n" + "="*50)
        print("ДИАГНОСТИКА РЕЗУЛЬТАТОВ АНАЛИЗА")
        print("="*50)
        
        total_docs = len(documents)
        print(f"Всего документов: {total_docs}")
        print(f"Обнаружено тем: {len(topic_stats)}")
        
        for i, topic in enumerate(topic_stats):
            print(f"\nТема #{i+1}: {topic['topic_name']}")
            print(f"  Документов: {topic['document_count']} ({topic['document_count']/total_docs*100:.1f}%)")
            print(f"  Уверенность: {topic['average_confidence']:.3f}")
            print(f"  Топ-5 ключевых слов: {', '.join(topic['keywords'][:5])}")
            
            # Показываем примеры документов из этой темы
            if topic['document_indices']:
                sample_idx = topic['document_indices'][0]
                if sample_idx < len(documents):
                    sample_text = documents[sample_idx][:100] + "..."
                    print(f"  Пример документа: {sample_text}")
    
    def get_fallback_result(self, documents):
        """
        Заглушка на случай ошибки анализа.
        """
        # Пытаемся определить темы эвристически
        themes = []
        for doc in documents:
            words = doc.lower().split()
            if any(word in words for word in ['хоккей', 'матч', 'гол', 'команда']):
                themes.append('спорт')
            elif any(word in words for word in ['технология', 'искусственный', 'интеллект', 'программа']):
                themes.append('технологии')
            elif any(word in words for word in ['финанс', 'рынок', 'инвестиц', 'экономик']):
                themes.append('финансы')
            else:
                themes.append('другое')
        
        from collections import Counter
        theme_counts = Counter(themes)
        
        topic_stats = []
        for idx, (theme, count) in enumerate(theme_counts.most_common()):
            topic_stats.append({
                'topic_id': idx,
                'topic_name': f"Тема {idx+1}: {theme}",
                'keywords': [theme],
                'document_count': count,
                'average_confidence': 0.8,
                'document_indices': [i for i, t in enumerate(themes) if t == theme]
            })
        
        return {
            'topic_statistics': topic_stats,
            'document_assignments': [],
            'topic_keywords': []
        }


class EnhancedBayesianAnalyzer(BayesianTopicAnalyzer):
    """
    Расширенный анализатор с интеллектуальным определением количества тем.
    """
    
    def __init__(self, max_topics=15, **kwargs):
        super().__init__(**kwargs)
        self.max_topics = max_topics
    
    def auto_determine_topics(self, documents, max_topics=None):
        """
        Интеллектуальное определение оптимального количества тем.
        """
        if max_topics is None:
            max_topics = self.max_topics
        
        if len(documents) < 5:
            # Для малого количества документов используем простую эвристику
            return min(3, max(2, len(documents) // 2))
        
        X, processed_docs = self.prepare_corpus(documents)
        
        # Ограничиваем максимальное количество тем
        max_possible = min(max_topics, X.shape[0] - 1, X.shape[1] // 10)
        max_possible = max(2, max_possible)
        
        print(f"Тестируем от 2 до {max_possible} тем...")
        
        perplexities = []
        topic_range = range(2, max_possible + 1)
        
        for n in topic_range:
            try:
                lda = LatentDirichletAllocation(
                    n_components=n,
                    random_state=42,
                    max_iter=30,
                    learning_method='online',
                    learning_offset=50.,
                    perp_tol=0.01
                )
                lda.fit(X)
                perplexity = lda.perplexity(X)
                perplexities.append(perplexity)
                print(f"  n={n}: perplexity={perplexity:.2f}")
            except Exception as e:
                perplexities.append(float('inf'))
                print(f"  n={n}: ошибка")
        
        # Находим "локоть" на кривой perplexity
        if len(perplexities) > 3:
            # Нормализуем perplexity
            perplexities_norm = [(p - min(perplexities)) / (max(perplexities) - min(perplexities)) 
                               for p in perplexities]
            
            # Вычисляем вторую производную
            second_derivatives = []
            for i in range(1, len(perplexities_norm) - 1):
                deriv = (perplexities_norm[i+1] - 2*perplexities_norm[i] + perplexities_norm[i-1])
                second_derivatives.append(abs(deriv))
            
            # Ищем точку максимального изгиба
            if second_derivatives:
                elbow_idx = np.argmax(second_derivatives) + 1
                best_n = topic_range[elbow_idx]
            else:
                best_n = min(5, max_possible)
        else:
            # Простая эвристика для малого диапазона
            best_n = min(4, max_possible)
        
        # Дополнительная эвристика на основе количества документов
        doc_based_topics = min(max_possible, max(2, len(documents) // 3))
        best_n = min(best_n, doc_based_topics)
        
        print(f"Выбрано оптимальное количество тем: {best_n}")
        return best_n
    
    def analyze_with_auto_topics(self, documents):
        """
        Анализ с автоматическим определением количества тем.
        """
        # Определяем оптимальное количество тем
        self.n_topics = self.auto_determine_topics(documents)
        
        # Устанавливаем TF-IDF для лучшего качества
        self.use_tfidf = True
        self.max_features = 3000  # Увеличиваем словарь
        
        print(f"\nЗапуск анализа с {self.n_topics} темами для {len(documents)} документов")
        return self.analyze_topics(documents)