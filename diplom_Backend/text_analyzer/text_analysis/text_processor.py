import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import re
from collections import Counter
import joblib
import os

class EnhancedTextProcessor:
    """
    Улучшенный предобработчик текста с тематическими словарями
    """
    
    def __init__(self):
        # Расширенные стоп-слова
        self.stop_words = self._load_stop_words()
        
        # Тематические словари
        self.theme_keywords = {
            'спорт': {
                'хоккей', 'футбол', 'баскетбол', 'теннис', 'волейбол', 'матч', 'гол',
                'команда', 'игрок', 'счет', 'победа', 'турнир', 'чемпионат', 'олимпиада',
                'спортсмен', 'тренер', 'стадион', 'лига', 'первенство', 'соревнование',
                'результат', 'тактика', 'стратегия', 'нападающий', 'защитник', 'вратарь'
            },
            'технологии': {
                'технология', 'искусственный', 'интеллект', 'программа', 'алгоритм',
                'компьютер', 'смартфон', 'приложение', 'интернет', 'данные', 'облачный',
                'цифровой', 'автоматизация', 'робот', 'сеть', 'сервер', 'база', 'разработка',
                'программирование', 'инновация', 'гаджет', 'устройство', 'операционная'
            },
            'финансы': {
                'финанс', 'экономик', 'рынок', 'инвестиц', 'деньги', 'банк', 'кредит',
                'акция', 'биржа', 'валюта', 'инфляция', 'бюджет', 'капитал', 'прибыль',
                'убыток', 'курс', 'дивиденд', 'облигация', 'трейдер', 'брокер', 'инвестор',
                'ликвидность', 'волатильность', 'дефолт', 'криптовалют'
            },
            'политика': {
                'правительство', 'президент', 'министр', 'парламент', 'выборы',
                'закон', 'реформа', 'демократия', 'дипломатия', 'международный',
                'санкция', 'переговоры', 'конституция', 'бюрократия', 'оппозиция'
            },
            'медицина': {
                'медицин', 'врач', 'пациент', 'лечение', 'диагноз', 'больница',
                'заболевание', 'симптом', 'терапия', 'операция', 'рецепт', 'вирус',
                'иммунитет', 'вакцина', 'эпидемия', 'пандемия', 'здоровье'
            }
        }
        
        # Синонимы для нормализации
        self.synonyms = {
            'айфон': 'смартфон',
            'ии': 'искусственный интеллект',
            'ai': 'искусственный интеллект',
            'блог': 'блоггер',
            'ксб': 'банк',
            'мобильник': 'смартфон',
            'ноут': 'ноутбук',
            'пк': 'компьютер',
            'соцсеть': 'социальная сеть',
            'фин': 'финанс',
            'экон': 'экономик',
            'инвест': 'инвестиц'
        }
    
    def _load_stop_words(self):
        """Загрузка расширенного списка стоп-слов"""
        base_stop_words = {
            'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все',
            'она', 'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по',
            'только', 'ее', 'мне', 'было', 'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из',
            'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг', 'ли', 'если', 'уже', 'или',
            'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж', 'вам',
            'ведь', 'там', 'потом', 'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где',
            'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем', 'была', 'сам', 'чтоб',
            'без', 'будто', 'чего', 'раз', 'тоже', 'себе', 'под', 'будет', 'ж', 'тогда',
            'кто', 'этот', 'того', 'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь',
            'этом', 'один', 'почти', 'мой', 'тем', 'чтобы', 'нее', 'сейчас', 'были', 'куда',
            'зачем', 'всех', 'никогда', 'можно', 'при', 'наконец', 'два', 'об', 'другой',
            'хоть', 'после', 'над', 'больше', 'тот', 'через', 'эти', 'нас', 'про', 'всего',
            'них', 'какая', 'много', 'разве', 'три', 'эту', 'моя', 'впрочем', 'хорошо',
            'свою', 'этой', 'перед', 'иногда', 'лучше', 'чуть', 'том', 'нельзя', 'такой',
            'им', 'более', 'всегда', 'конечно', 'всю', 'между'
        }
        return base_stop_words
    
    def normalize_text(self, text):
        """Нормализация текста с учетом тематик"""
        text = text.lower()
        
        # Замена синонимов
        for wrong, correct in self.synonyms.items():
            text = re.sub(rf'\b{wrong}\b', correct, text)
        
        # Удаление лишних символов, но сохранение важных
        text = re.sub(r'[^\w\s\.\,\-\:\+\%\$\€\£]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_key_terms(self, text, max_terms=20):
        """Извлечение ключевых терминов с учетом тематик"""
        words = text.split()
        
        # Взвешивание слов по тематическим словарям
        weighted_terms = []
        for word in words:
            if len(word) < 3 or word in self.stop_words:
                continue
            
            weight = 1.0
            
            # Повышаем вес тематических терминов
            for theme, keywords in self.theme_keywords.items():
                if any(keyword in word for keyword in keywords):
                    weight *= 2.0  # Удваиваем вес для тематических слов
            
            # Повышаем вес редких слов (предполагаем, что они более информативны)
            if len(word) > 6:
                weight *= 1.5
            
            weighted_terms.append((word, weight))
        
        # Сортируем по весу
        weighted_terms.sort(key=lambda x: x[1], reverse=True)
        
        # Берем топ-N терминов
        top_terms = [term for term, _ in weighted_terms[:max_terms]]
        
        return ' '.join(top_terms)
    
    def process_document(self, text):
        """Полная обработка документа"""
        normalized = self.normalize_text(text)
        key_terms = self.extract_key_terms(normalized)
        return key_terms
    
    def guess_theme(self, text):
        """Предварительное определение темы по ключевым словам"""
        normalized = self.normalize_text(text)
        words = normalized.split()
        
        theme_scores = {}
        for theme, keywords in self.theme_keywords.items():
            score = sum(1 for word in words if any(keyword in word for keyword in keywords))
            theme_scores[theme] = score
        
        if theme_scores:
            main_theme = max(theme_scores.items(), key=lambda x: x[1])
            if main_theme[1] > 0:
                return main_theme[0]
        
        return 'другое'


class HybridTopicAnalyzer:
    """
    Гибридный анализатор тем с несколькими алгоритмами
    """
    
    def __init__(self, models_dir='models'):
        self.processor = EnhancedTextProcessor()
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
        
        # Параметры алгоритмов
        self.lda_params = {
            'n_components': 5,
            'max_iter': 100,
            'learning_method': 'online',
            'random_state': 42
        }
        
        self.nmf_params = {
            'n_components': 5,
            'random_state': 42,
            'beta_loss': 'frobenius',
            'max_iter': 1000
        }
        
        self.vectorizer_params = {
            'max_features': 5000,
            'min_df': 2,
            'max_df': 0.95,
            'ngram_range': (1, 3),
            'stop_words': list(self.processor.stop_words)
        }
        
        self.models = {}
        
    def prepare_corpus(self, documents, use_cache=True):
        """Подготовка корпуса с кэшированием"""
        cache_file = os.path.join(self.models_dir, 'corpus_cache.pkl')
        
        if use_cache and os.path.exists(cache_file):
            print("Загрузка корпуса из кэша...")
            return joblib.load(cache_file)
        
        print("Обработка документов...")
        processed_docs = [self.processor.process_document(doc) for doc in documents]
        
        # TF-IDF векторизация
        vectorizer = TfidfVectorizer(**self.vectorizer_params)
        X = vectorizer.fit_transform(processed_docs)
        feature_names = vectorizer.get_feature_names_out()
        
        result = {
            'X': X,
            'feature_names': feature_names,
            'processed_docs': processed_docs,
            'vectorizer': vectorizer
        }
        
        if use_cache:
            joblib.dump(result, cache_file)
            print(f"Корпус сохранен в кэш: {cache_file}")
        
        return result
    
    def train_lda(self, X, n_topics=None):
        """Обучение LDA модели"""
        if n_topics is None:
            n_topics = self.lda_params['n_components']
        
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            max_iter=self.lda_params['max_iter'],
            learning_method=self.lda_params['learning_method'],
            random_state=self.lda_params['random_state'],
            verbose=1
        )
        
        lda.fit(X)
        return lda
    
    def train_nmf(self, X, n_topics=None):
        """Обучение NMF модели"""
        if n_topics is None:
            n_topics = self.nmf_params['n_components']
        
        nmf = NMF(
            n_components=n_topics,
            random_state=self.nmf_params['random_state'],
            beta_loss=self.nmf_params['beta_loss'],
            max_iter=self.nmf_params['max_iter'],
            verbose=1
        )
        
        nmf.fit(X)
        return nmf
    
    def find_optimal_topics(self, X, max_topics=15):
        """Поиск оптимального количества тем"""
        print("\nПоиск оптимального количества тем...")
        
        silhouette_scores = []
        topic_range = range(2, min(max_topics, X.shape[0] - 1, X.shape[1] // 20) + 1)
        
        for n in topic_range:
            try:
                # Обучаем KMeans для оценки
                kmeans = KMeans(n_clusters=n, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(X.toarray())
                
                # Вычисляем силуэтный коэффициент
                if len(set(cluster_labels)) > 1:
                    score = silhouette_score(X.toarray(), cluster_labels)
                else:
                    score = -1
                
                silhouette_scores.append(score)
                print(f"  n={n}: silhouette={score:.4f}")
                
            except Exception as e:
                silhouette_scores.append(-1)
                print(f"  n={n}: ошибка")
        
        # Находим оптимальное количество тем
        if silhouette_scores:
            best_idx = np.argmax(silhouette_scores)
            best_n = topic_range[best_idx]
            print(f"\nОптимальное количество тем: {best_n} (silhouette={silhouette_scores[best_idx]:.4f})")
            return best_n
        
        # Эвристика по умолчанию
        default_n = min(8, max(3, X.shape[0] // 5))
        print(f"\nИспользуем эвристику: {default_n} тем")
        return default_n
    
    def extract_topic_keywords(self, model, feature_names, n_keywords=15, model_type='lda'):
        """Извлечение ключевых слов для тем"""
        topic_keywords = []
        
        if model_type == 'lda':
            components = model.components_
        elif model_type == 'nmf':
            components = model.components_
        else:
            raise ValueError(f"Неизвестный тип модели: {model_type}")
        
        for topic_idx, topic in enumerate(components):
            # Получаем топ ключевых слов
            top_indices = topic.argsort()[:-n_keywords-1:-1]
            keywords = [feature_names[i] for i in top_indices]
            
            # Анализируем тему по ключевым словам
            theme_guess = self._guess_topic_theme(keywords)
            
            topic_info = {
                'topic_id': topic_idx,
                'keywords': keywords,
                'theme_guess': theme_guess,
                'topic_name': self._generate_topic_name(keywords, theme_guess)
            }
            topic_keywords.append(topic_info)
        
        return topic_keywords
    
    def _guess_topic_theme(self, keywords):
        """Определение тематики по ключевым словам"""
        theme_scores = {}
        
        for theme, theme_keywords in self.processor.theme_keywords.items():
            score = 0
            for keyword in keywords[:10]:  # Смотрим только топ-10 ключевых слов
                if any(theme_kw in keyword for theme_kw in theme_keywords):
                    score += 1
            theme_scores[theme] = score
        
        # Добавляем оценку для "другой" темы
        theme_scores['другое'] = max(0, 10 - max(theme_scores.values()))
        
        return max(theme_scores.items(), key=lambda x: x[1])[0]
    
    def _generate_topic_name(self, keywords, theme):
        """Генерация понятного названия темы"""
        # Берем наиболее информативные слова (не слишком частые и не слишком редкие)
        if len(keywords) >= 3:
            # Предпочитаем слова средней позиции в списке
            mid_idx = len(keywords) // 2
            name_words = [keywords[0], keywords[mid_idx]]
            
            # Добавляем тематическое слово, если его нет
            theme_words = list(self.processor.theme_keywords.get(theme, []))
            if theme_words:
                for theme_word in theme_words[:3]:
                    if theme_word not in ' '.join(name_words).lower():
                        name_words.append(theme_word)
                        break
            
            topic_name = f"{theme.capitalize()}: {', '.join(name_words[:3])}"
        else:
            topic_name = f"{theme.capitalize()}: {', '.join(keywords[:3])}"
        
        return topic_name
    
    def assign_documents_to_topics(self, model, X, model_type='lda'):
        """Распределение документов по темам"""
        if model_type == 'lda':
            topic_dist = model.transform(X)
        elif model_type == 'nmf':
            topic_dist = model.transform(X)
        else:
            raise ValueError(f"Неизвестный тип модели: {model_type}")
        
        assignments = []
        for doc_idx, dist in enumerate(topic_dist):
            dominant_topic = np.argmax(dist)
            confidence = dist[dominant_topic]
            
            # Если уверенность низкая, ищем вторую возможную тему
            secondary_topic = -1
            if confidence < 0.3:
                sorted_topics = np.argsort(dist)[::-1]
                if len(sorted_topics) > 1:
                    secondary_topic = sorted_topics[1]
            
            assignments.append({
                'document_index': doc_idx,
                'dominant_topic': dominant_topic,
                'confidence': float(confidence),
                'secondary_topic': int(secondary_topic),
                'topic_distribution': dist.tolist()
            })
        
        return assignments
    
    def ensemble_analysis(self, documents, use_cache=True):
        """
        Ансамблевый анализ с использованием нескольких алгоритмов
        """
        print("=" * 60)
        print("ГИБРИДНЫЙ АНАЛИЗ ТЕМАТИК")
        print("=" * 60)
        
        # Подготовка данных
        corpus_data = self.prepare_corpus(documents, use_cache)
        X = corpus_data['X']
        feature_names = corpus_data['feature_names']
        
        # Определение оптимального количества тем
        optimal_topics = self.find_optimal_topics(X)
        self.lda_params['n_components'] = optimal_topics
        self.nmf_params['n_components'] = optimal_topics
        
        # Обучение LDA
        print("\n" + "=" * 30)
        print("ОБУЧЕНИЕ LDA МОДЕЛИ")
        print("=" * 30)
        lda_model = self.train_lda(X)
        
        # Обучение NMF
        print("\n" + "=" * 30)
        print("ОБУЧЕНИЕ NMF МОДЕЛИ")
        print("=" * 30)
        nmf_model = self.train_nmf(X)
        
        # Извлечение ключевых слов
        lda_keywords = self.extract_topic_keywords(lda_model, feature_names, model_type='lda')
        nmf_keywords = self.extract_topic_keywords(nmf_model, feature_names, model_type='nmf')
        
        # Распределение документов
        lda_assignments = self.assign_documents_to_topics(lda_model, X, 'lda')
        nmf_assignments = self.assign_documents_to_topics(nmf_model, X, 'nmf')
        
        # Консенсусное распределение
        consensus_assignments = self._create_consensus_assignments(
            lda_assignments, nmf_assignments, optimal_topics
        )
        
        # Статистика по темам
        lda_stats = self._calculate_topic_statistics(lda_assignments, lda_keywords)
        nmf_stats = self._calculate_topic_statistics(nmf_assignments, nmf_keywords)
        consensus_stats = self._calculate_topic_statistics(consensus_assignments, lda_keywords)
        
        # Сохранение моделей
        self.models['lda'] = lda_model
        self.models['nmf'] = nmf_model
        self.models['vectorizer'] = corpus_data['vectorizer']
        
        # Формирование результатов
        results = {
            'lda': {
                'topic_statistics': lda_stats,
                'keywords': lda_keywords,
                'assignments': lda_assignments,
                'model': lda_model
            },
            'nmf': {
                'topic_statistics': nmf_stats,
                'keywords': nmf_keywords,
                'assignments': nmf_assignments,
                'model': nmf_model
            },
            'consensus': {
                'topic_statistics': consensus_stats,
                'keywords': lda_keywords,  # Используем LDA ключевые слова для консенсуса
                'assignments': consensus_assignments
            },
            'metadata': {
                'total_documents': len(documents),
                'optimal_topics': optimal_topics,
                'vocabulary_size': len(feature_names),
                'processing_time': 'реальное время можно добавить'
            }
        }
        
        # Вывод диагностической информации
        self._print_diagnostics(results, documents)
        
        return results
    
    def _create_consensus_assignments(self, lda_assignments, nmf_assignments, n_topics):
        """Создание консенсусного распределения документов"""
        consensus = []
        
        for lda_assignment, nmf_assignment in zip(lda_assignments, nmf_assignments):
            doc_idx = lda_assignment['document_index']
            
            # Если оба алгоритма согласны
            if (lda_assignment['dominant_topic'] == nmf_assignment['dominant_topic'] and
                lda_assignment['confidence'] > 0.3 and nmf_assignment['confidence'] > 0.3):
                dominant_topic = lda_assignment['dominant_topic']
                confidence = (lda_assignment['confidence'] + nmf_assignment['confidence']) / 2
            else:
                # Используем распределение с большей уверенностью
                if lda_assignment['confidence'] > nmf_assignment['confidence']:
                    dominant_topic = lda_assignment['dominant_topic']
                    confidence = lda_assignment['confidence']
                else:
                    dominant_topic = nmf_assignment['dominant_topic']
                    confidence = nmf_assignment['confidence']
            
            consensus.append({
                'document_index': doc_idx,
                'dominant_topic': dominant_topic,
                'confidence': confidence,
                'secondary_topic': -1,
                'topic_distribution': [0] * n_topics
            })
        
        return consensus
    
    def _calculate_topic_statistics(self, assignments, topic_keywords):
        """Расчет статистики по темам"""
        n_topics = len(topic_keywords)
        topic_docs = [[] for _ in range(n_topics)]
        
        for assignment in assignments:
            topic_id = assignment['dominant_topic']
            if 0 <= topic_id < n_topics:
                topic_docs[topic_id].append(assignment)
        
        stats = []
        for topic_id in range(n_topics):
            docs = topic_docs[topic_id]
            topic_info = topic_keywords[topic_id]
            
            if docs:
                avg_confidence = np.mean([doc['confidence'] for doc in docs])
            else:
                avg_confidence = 0
            
            stats.append({
                'topic_id': topic_id,
                'topic_name': topic_info['topic_name'],
                'theme_guess': topic_info['theme_guess'],
                'keywords': topic_info['keywords'],
                'document_count': len(docs),
                'average_confidence': round(avg_confidence, 3),
                'document_indices': [doc['document_index'] for doc in docs]
            })
        
        # Сортируем по количеству документов
        stats.sort(key=lambda x: x['document_count'], reverse=True)
        
        return stats
    
    def _print_diagnostics(self, results, documents):
        """Вывод диагностической информации"""
        print("\n" + "=" * 60)
        print("ДИАГНОСТИЧЕСКАЯ ИНФОРМАЦИЯ")
        print("=" * 60)
        
        metadata = results['metadata']
        consensus_stats = results['consensus']['topic_statistics']
        
        print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"  • Всего документов: {metadata['total_documents']}")
        print(f"  • Оптимальное количество тем: {metadata['optimal_topics']}")
        print(f"  • Размер словаря: {metadata['vocabulary_size']}")
        
        print(f"\n🎯 КОНСЕНСУСНЫЕ ТЕМЫ:")
        for i, topic in enumerate(consensus_stats[:10]):  # Показываем топ-10 тем
            if topic['document_count'] > 0:
                print(f"\n  Тема #{i+1}: {topic['topic_name']}")
                print(f"    • Предполагаемая тематика: {topic['theme_guess']}")
                print(f"    • Документов: {topic['document_count']}")
                print(f"    • Уверенность: {topic['average_confidence']:.3f}")
                print(f"    • Ключевые слова: {', '.join(topic['keywords'][:5])}")
        
        # Показываем распределение по темам
        print(f"\n📈 РАСПРЕДЕЛЕНИЕ ДОКУМЕНТОВ ПО ТЕМАМ:")
        for topic in consensus_stats:
            if topic['document_count'] > 0:
                percentage = (topic['document_count'] / metadata['total_documents']) * 100
                print(f"  • {topic['topic_name']}: {topic['document_count']} документов ({percentage:.1f}%)")
    
    def save_models(self):
        """Сохранение обученных моделей"""
        for name, model in self.models.items():
            filename = os.path.join(self.models_dir, f'{name}_model.pkl')
            joblib.dump(model, filename)
            print(f"Модель {name} сохранена в {filename}")
    
    def load_models(self):
        """Загрузка обученных моделей"""
        for name in ['lda', 'nmf', 'vectorizer']:
            filename = os.path.join(self.models_dir, f'{name}_model.pkl')
            if os.path.exists(filename):
                self.models[name] = joblib.load(filename)
                print(f"Модель {name} загружена из {filename}")


class TrainedTopicAnalyzer:
    """
    Анализатор с предобученными моделями на различных тематиках
    """
    
    def __init__(self):
        self.hybrid_analyzer = HybridTopicAnalyzer()
        self.theme_classifier = ThemeClassifier()
        
    def analyze_with_training(self, documents, train_new=False):
        """
        Анализ с возможностью дообучения на новых данных
        """
        if train_new or not os.path.exists(os.path.join(self.hybrid_analyzer.models_dir, 'lda_model.pkl')):
            print("🔄 Обучение новых моделей на предоставленных данных...")
            results = self.hybrid_analyzer.ensemble_analysis(documents)
            self.hybrid_analyzer.save_models()
        else:
            print("📂 Загрузка предобученных моделей...")
            self.hybrid_analyzer.load_models()
            
            # Подготовка новых данных
            corpus_data = self.hybrid_analyzer.prepare_corpus(documents, use_cache=False)
            X = corpus_data['X']
            feature_names = corpus_data['feature_names']
            
            # Используем загруженные модели
            lda_model = self.hybrid_analyzer.models['lda']
            nmf_model = self.hybrid_analyzer.models['nmf']
            
            # Анализ с существующими моделями
            lda_keywords = self.hybrid_analyzer.extract_topic_keywords(
                lda_model, feature_names, model_type='lda'
            )
            lda_assignments = self.hybrid_analyzer.assign_documents_to_topics(
                lda_model, X, 'lda'
            )
            lda_stats = self.hybrid_analyzer._calculate_topic_statistics(
                lda_assignments, lda_keywords
            )
            
            results = {
                'topic_statistics': lda_stats,
                'keywords': lda_keywords,
                'assignments': lda_assignments,
                'metadata': {
                    'total_documents': len(documents),
                    'model_type': 'pre-trained LDA'
                }
            }
        
        return results


class ThemeClassifier:
    """
    Классификатор тем на основе правил и ML
    """
    
    def __init__(self):
        self.rules = self._build_classification_rules()
        
    def _build_classification_rules(self):
        """Построение правил для классификации тем"""
        rules = {
            'спорт': [
                (['хоккей', 'матч', 'гол', 'команда'], 2.0),
                (['футбол', 'гол', 'пенальти', 'офсайд'], 2.0),
                (['баскетбол', 'трехочковый', 'данк', 'подбор'], 2.0),
                (['теннис', 'эйс', 'сет', 'гейм'], 2.0),
                (['олимпийский', 'медаль', 'рекорд', 'соревнование'], 1.5)
            ],
            'технологии': [
                (['искусственный интеллект', 'нейросеть', 'машинное обучение'], 3.0),
                (['смартфон', 'гаджет', 'приложение', 'обновление'], 2.0),
                (['программирование', 'алгоритм', 'код', 'разработка'], 2.0),
                (['интернет', 'сеть', 'онлайн', 'цифровой'], 1.5)
            ],
            'финансы': [
                (['акция', 'биржа', 'инвестиция', 'трейдер'], 2.5),
                (['банк', 'кредит', 'ипотека', 'вклад'], 2.0),
                (['криптовалюта', 'биткоин', 'блокчейн'], 2.5),
                (['экономика', 'инфляция', 'валюта', 'рынок'], 2.0)
            ]
        }
        return rules
    
    def classify_document(self, text, keywords=None):
        """Классификация документа по темам"""
        text_lower = text.lower()
        
        theme_scores = {}
        
        # Применяем правила
        for theme, theme_rules in self.rules.items():
            score = 0
            for keywords_list, weight in theme_rules:
                keyword_count = sum(1 for keyword in keywords_list if keyword in text_lower)
                score += keyword_count * weight
            
            # Учитываем ключевые слова из LDA/NMF анализа
            if keywords:
                for keyword in keywords[:10]:
                    for theme_rules_keywords, _ in self.rules.get(theme, []):
                        if any(kw in keyword for kw in theme_rules_keywords):
                            score += 1
            
            theme_scores[theme] = score
        
        # Нормализуем scores
        total_score = sum(theme_scores.values())
        if total_score > 0:
            theme_scores = {k: v/total_score for k, v in theme_scores.items()}
        
        # Определяем основную тему
        if theme_scores:
            main_theme = max(theme_scores.items(), key=lambda x: x[1])
            if main_theme[1] > 0.1:  # Порог уверенности
                return {
                    'main_theme': main_theme[0],
                    'confidence': main_theme[1],
                    'all_scores': theme_scores
                }
        
        return {
            'main_theme': 'другое',
            'confidence': 1.0,
            'all_scores': {'другое': 1.0}
        }


# Фабричный метод для создания анализатора
def create_analyzer(mode='hybrid'):
    """
    Создание анализатора в зависимости от режима
    
    Аргументы:
        mode: 'hybrid' - гибридный анализ (LDA + NMF)
              'trained' - с предобученными моделями
              'simple' - простой LDA анализатор
    """
    if mode == 'hybrid':
        return HybridTopicAnalyzer()
    elif mode == 'trained':
        return TrainedTopicAnalyzer()
    elif mode == 'simple':
        from .bayesian_analyzer import EnhancedBayesianAnalyzer
        return EnhancedBayesianAnalyzer()
    else:
        raise ValueError(f"Неизвестный режим: {mode}")