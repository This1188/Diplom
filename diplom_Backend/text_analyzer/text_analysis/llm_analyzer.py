import requests
import json
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
import asyncio
import aiohttp
from dataclasses import dataclass
from enum import Enum
import hashlib
import pickle
import os
from pathlib import Path

class LLMProvider(Enum):
    OLLAMA = "ollama"
    YANDEX_GPT = "yandex_gpt"
    OPENAI = "openai"

@dataclass
class Document:
    id: str
    date: str
    theme: str
    text: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class Topic:
    id: int
    name: str
    description: str
    keywords: List[str]
    documents: List[Document]
    confidence: float
    category: str = "general"
    
    def to_dict(self):
        return {
            "topic_id": self.id,
            "topic_name": self.name,
            "description": self.description,
            "keywords": self.keywords,
            "document_count": len(self.documents),
            "confidence": self.confidence,
            "category": self.category,
            "document_indices": [doc.id for doc in self.documents]
        }

class LLMTopicAnalyzer:
    """
    Анализатор тем на основе LLM (Ollama с русскоязычной моделью)
    """
    
    def __init__(self, 
                 provider: LLMProvider = LLMProvider.OLLAMA,
                 model_name: str = "mistral",
                 ollama_url: str = "http://localhost:11434",
                 cache_dir: str = ".llm_cache"):
        """
        Инициализация анализатора
        
        Args:
            provider: Провайдер LLM
            model_name: Название модели
            ollama_url: URL для Ollama API
            cache_dir: Директория для кэша
        """
        self.provider = provider
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Промпты для разных задач
        self.prompts = {
            "topic_extraction": """Ты - эксперт по анализу текстов. Проанализируй следующие документы и определи основные темы.

Документы:
{documents}

Задачи:
1. Определи 3-5 основных тем, которые охватывают эти документы
2. Для каждой темы дай:
   - Название темы (лаконичное, информативное)
   - Описание темы (2-3 предложения)
   - 5-7 ключевых слов
   - Оценку уверенности в теме (0-1)
3. Распредели документы по темам

Формат ответа в JSON:
{{
  "topics": [
    {{
      "id": 1,
      "name": "Название темы",
      "description": "Описание темы",
      "keywords": ["слово1", "слово2", ...],
      "confidence": 0.95,
      "document_ids": ["doc1", "doc2", ...]
    }}
  ]
}}

Ответ только в формате JSON, без дополнительного текста.""",
            
            "topic_refinement": """Ты - эксперт по тематической классификации. Уточни темы для следующего набора документов.

Существующие темы:
{existing_topics}

Новые документы для анализа:
{new_documents}

Задачи:
1. Обнови существующие темы или добавь новые, если нужно
2. Для каждой темы уточни:
   - Название
   - Описание
   - Ключевые слова
3. Распредели новые документы по темам

Формат ответа в JSON:
{{
  "updated_topics": [
    {{
      "id": 1,
      "name": "Обновленное название",
      "description": "Обновленное описание",
      "keywords": ["новое_слово1", ...],
      "confidence": 0.92,
      "document_ids": ["doc1", "doc3", "new_doc1", ...]
    }}
  ]
}}""",
            
            "single_document_analysis": """Проанализируй документ и определи его основную тему.

Документ:
Тема: {theme}
Дата: {date}
Текст: {text}

Задачи:
1. Определи основную тему документа (1-2 слова)
2. Дай краткое описание темы
3. Укажи 3-5 ключевых слов
4. Оцени уверенность (0-1)

Формат ответа в JSON:
{{
  "document_id": "{doc_id}",
  "main_topic": "Название темы",
  "topic_description": "Описание",
  "keywords": ["слово1", "слово2", ...],
  "confidence": 0.88
}}""",
            
            "summary_generation": """Сформируй подробную справку по теме за указанный период.

Тема: {topic_name}
Описание: {topic_description}
Период: {start_date} - {end_date}
Ключевые слова: {keywords}
Документы в теме ({count} шт.):

{documents_summary}

Задачи:
1. Сформируй аналитическую справку по теме
2. Выдели основные тренды и закономерности
3. Укажи ключевые события и изменения
4. Дай рекомендации или выводы

Формат ответа (развернутый текст):
# Аналитическая справка по теме: {topic_name}

## Основные тренды
...

## Ключевые события
...

## Анализ динамики
...

## Выводы и рекомендации
..."""
        }
    
    def _get_cache_key(self, documents: List[Document], task: str) -> str:
        """Генерация ключа для кэша"""
        content = f"{task}_{self.model_name}_{len(documents)}"
        for doc in documents[:5]:  # Используем первые 5 документов для уникальности
            content += f"_{doc.id}_{hashlib.md5(doc.text.encode()).hexdigest()[:10]}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Загрузка из кэша"""
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Сохранение в кэш"""
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)
    
    async def _call_llm_async(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """
        Асинхронный вызов LLM через Ollama API
        """
        if self.provider == LLMProvider.OLLAMA:
            url = f"{self.ollama_url}/api/generate"
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_predict": 4000
                }
            }
            
            for attempt in range(max_retries):
                try:
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120)) as session:
                        async with session.post(url, json=payload) as response:
                            if response.status == 200:
                                result = await response.json()
                                return result.get("response", "")
                            else:
                                print(f"Attempt {attempt + 1} failed: {response.status}")
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                except Exception as e:
                    print(f"Attempt {attempt + 1} error: {e}")
                    await asyncio.sleep(2 ** attempt)
            
            return None
        
        elif self.provider == LLMProvider.YANDEX_GPT:
            # Реализация для Yandex GPT API
            # Требуется API ключ от Yandex Cloud
            pass
        
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _call_llm_sync(self, prompt: str) -> Optional[str]:
        """
        Синхронный вызов LLM (обертка для асинхронного)
        """
        try:
            return asyncio.run(self._call_llm_async(prompt))
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return None
    
    def _parse_llm_response(self, response: str) -> Dict:
        """
        Парсинг ответа LLM, извлечение JSON
        """
        if not response:
            return {}
        
        # Ищем JSON в ответе
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                print(f"Raw response: {response[:500]}...")
        
        # Если JSON не найден, пытаемся извлечь структурированные данные
        return self._extract_structured_data(response)
    
    def _extract_structured_data(self, text: str) -> Dict:
        """
        Извлечение структурированных данных из текстового ответа
        """
        result = {"topics": []}
        
        # Простая эвристика для извлечения тем
        lines = text.split('\n')
        current_topic = None
        
        for line in lines:
            line = line.strip()
            
            # Поиск названия темы
            if line.startswith("Тема") or line.startswith("Topic") or ":" in line and len(line) < 100:
                if current_topic and "name" in current_topic:
                    result["topics"].append(current_topic)
                
                current_topic = {
                    "name": line.split(":")[-1].strip() if ":" in line else line,
                    "keywords": [],
                    "description": "",
                    "confidence": 0.8
                }
            
            # Поиск ключевых слов
            elif "ключевые слова" in line.lower() or "keywords" in line.lower():
                if current_topic:
                    words = re.findall(r'\b[\w\-]+\b', line)
                    current_topic["keywords"] = words[1:] if words else []
            
            # Поиск описания
            elif current_topic and not current_topic["description"] and len(line) > 20:
                current_topic["description"] = line
        
        if current_topic and "name" in current_topic:
            result["topics"].append(current_topic)
        
        return result
    
    def _prepare_documents_for_prompt(self, documents: List[Document]) -> str:
        """
        Подготовка документов для промпта
        """
        formatted_docs = []
        for i, doc in enumerate(documents, 1):
            summary = doc.text[:200] + "..." if len(doc.text) > 200 else doc.text
            formatted_docs.append(
                f"Документ {i} (ID: {doc.id}, Дата: {doc.date}, Тема: {doc.theme}):\n"
                f"{summary}"
            )
        return "\n\n".join(formatted_docs)
    
    def analyze_topics(self, documents: List[Document], use_cache: bool = True) -> Dict:
        """
        Основной метод анализа тем с помощью LLM
        """
        if not documents:
            return {"topics": [], "metadata": {"total_documents": 0}}
        
        # Проверка кэша
        cache_key = self._get_cache_key(documents, "topic_extraction")
        if use_cache:
            cached = self._load_from_cache(cache_key)
            if cached:
                print("Using cached results")
                return cached
        
        # Подготовка промпта
        formatted_docs = self._prepare_documents_for_prompt(documents)
        prompt = self.prompts["topic_extraction"].format(documents=formatted_docs)
        
        print(f"Analyzing {len(documents)} documents with LLM...")
        print(f"Using model: {self.model_name}")
        
        # Вызов LLM
        response = self._call_llm_sync(prompt)
        
        if not response:
            print("LLM call failed, using fallback")
            return self._fallback_analysis(documents)
        
        # Парсинг ответа
        result = self._parse_llm_response(response)
        
        # Обогащение результата
        enriched_result = self._enrich_analysis_result(result, documents)
        
        # Сохранение в кэш
        if use_cache:
            self._save_to_cache(cache_key, enriched_result)
        
        return enriched_result
    
    def _enrich_analysis_result(self, llm_result: Dict, documents: List[Document]) -> Dict:
        """
        Обогащение результата анализа
        """
        # Создаем словарь документов по ID
        doc_dict = {doc.id: doc for doc in documents}
        
        topics = []
        for i, topic_data in enumerate(llm_result.get("topics", [])):
            # Получаем документы для темы
            topic_docs = []
            for doc_id in topic_data.get("document_ids", []):
                if doc_id in doc_dict:
                    topic_docs.append(doc_dict[doc_id])
                else:
                    # Если ID не найден, пытаемся сопоставить по индексу
                    try:
                        idx = int(doc_id.replace("doc", "")) - 1
                        if 0 <= idx < len(documents):
                            topic_docs.append(documents[idx])
                    except:
                        pass
            
            # Если нет документов, пытаемся определить по ключевым словам
            if not topic_docs and "keywords" in topic_data:
                for doc in documents:
                    doc_text = doc.text.lower()
                    if any(keyword.lower() in doc_text for keyword in topic_data["keywords"][:3]):
                        topic_docs.append(doc)
            
            # Создаем объект Topic
            topic = Topic(
                id=i + 1,
                name=topic_data.get("name", f"Тема {i + 1}"),
                description=topic_data.get("description", ""),
                keywords=topic_data.get("keywords", []),
                documents=topic_docs,
                confidence=topic_data.get("confidence", 0.7),
                category=self._categorize_topic(topic_data)
            )
            topics.append(topic)
        
        # Если LLM не распределил документы, делаем это сами
        if not any(t.documents for t in topics):
            topics = self._distribute_documents_to_topics(topics, documents)
        
        # Форматируем результат
        result = {
            "topics": [topic.to_dict() for topic in topics],
            "metadata": {
                "total_documents": len(documents),
                "topics_discovered": len(topics),
                "model_used": self.model_name,
                "provider": self.provider.value,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        return result
    
    def _categorize_topic(self, topic_data: Dict) -> str:
        """Категоризация темы"""
        name = topic_data.get("name", "").lower()
        keywords = [k.lower() for k in topic_data.get("keywords", [])]
        description = topic_data.get("description", "").lower()
        
        all_text = name + " " + " ".join(keywords) + " " + description
        
        categories = {
            "спорт": ["хоккей", "футбол", "матч", "команда", "игрок", "гол", "спорт", "соревнование"],
            "технологии": ["технолог", "искусствен", "интеллект", "программ", "алгоритм", "данные", "цифровой"],
            "финансы": ["финанс", "экономик", "рынок", "инвестиц", "банк", "акция", "деньги"],
            "политика": ["политик", "правительств", "президент", "закон", "выборы", "международный"],
            "медицина": ["медицин", "врач", "здоровье", "лечение", "заболевание", "больница"],
            "образование": ["образовани", "университет", "студент", "обучение", "школа", "курс"],
            "культура": ["культур", "искусство", "кино", "музыка", "театр", "литература"]
        }
        
        for category, keywords_list in categories.items():
            if any(keyword in all_text for keyword in keywords_list):
                return category
        
        return "general"
    
    def _distribute_documents_to_topics(self, topics: List[Topic], documents: List[Document]) -> List[Topic]:
        """
        Распределение документов по темам на основе ключевых слов
        """
        # Сбрасываем документы в темах
        for topic in topics:
            topic.documents = []
        
        # Распределяем каждый документ
        for doc in documents:
            doc_text = doc.text.lower()
            best_topic = None
            best_score = 0
            
            for topic in topics:
                score = 0
                # Оцениваем по ключевым словам
                for keyword in topic.keywords:
                    if keyword.lower() in doc_text:
                        score += 1
                
                # Оцениваем по названию темы
                for word in topic.name.lower().split():
                    if word in doc_text and len(word) > 3:
                        score += 2
                
                if score > best_score:
                    best_score = score
                    best_topic = topic
            
            # Если нашли подходящую тему, добавляем документ
            if best_topic and best_score > 0:
                best_topic.documents.append(doc)
            else:
                # Создаем новую тему для неклассифицированных документов
                unclassified_topic = next((t for t in topics if t.name == "Другое"), None)
                if not unclassified_topic:
                    unclassified_topic = Topic(
                        id=len(topics) + 1,
                        name="Другое",
                        description="Разные темы",
                        keywords=["разное", "другое"],
                        documents=[],
                        confidence=0.5,
                        category="general"
                    )
                    topics.append(unclassified_topic)
                unclassified_topic.documents.append(doc)
        
        return topics
    
    def _fallback_analysis(self, documents: List[Document]) -> Dict:
        """
        Фолбэк анализ, если LLM недоступен
        """
        print("Using fallback analysis")
        
        # Простая кластеризация по ключевым словам
        from collections import Counter
        import re
        
        # Извлекаем ключевые слова из документов
        all_keywords = []
        for doc in documents:
            words = re.findall(r'\b[а-яё]{4,}\b', doc.text.lower())
            common_words = {'этот', 'который', 'очень', 'много', 'также', 'после', 'перед'}
            keywords = [w for w in words if w not in common_words]
            all_keywords.extend(keywords[:10])  # Берем топ-10 слов из каждого документа
        
        # Находим наиболее частые тематические слова
        word_counts = Counter(all_keywords)
        common_themes = word_counts.most_common(5)
        
        # Создаем темы
        topics = []
        for i, (theme_word, _) in enumerate(common_themes):
            # Находим документы с этим словом
            theme_docs = []
            for doc in documents:
                if theme_word in doc.text.lower():
                    theme_docs.append(doc)
            
            if theme_docs:
                topic = Topic(
                    id=i + 1,
                    name=f"Тема: {theme_word.capitalize()}",
                    description=f"Документы связанные с {theme_word}",
                    keywords=[theme_word] + [w for w, _ in word_counts.most_common(10) if w != theme_word][:4],
                    documents=theme_docs,
                    confidence=0.6,
                    category=self._categorize_topic({"name": theme_word, "keywords": [theme_word]})
                )
                topics.append(topic)
        
        # Группируем оставшиеся документы
        assigned_docs = set()
        for topic in topics:
            assigned_docs.update(doc.id for doc in topic.documents)
        
        unassigned_docs = [doc for doc in documents if doc.id not in assigned_docs]
        if unassigned_docs:
            other_topic = Topic(
                id=len(topics) + 1,
                name="Другие темы",
                description="Различные документы",
                keywords=["разное", "другое"],
                documents=unassigned_docs,
                confidence=0.5,
                category="general"
            )
            topics.append(other_topic)
        
        return {
            "topics": [topic.to_dict() for topic in topics],
            "metadata": {
                "total_documents": len(documents),
                "topics_discovered": len(topics),
                "model_used": "fallback",
                "provider": "fallback",
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def analyze_single_document(self, document: Document) -> Dict:
        """
        Анализ одного документа
        """
        prompt = self.prompts["single_document_analysis"].format(
            theme=document.theme,
            date=document.date,
            text=document.text[:1000],  # Ограничиваем длину
            doc_id=document.id
        )
        
        response = self._call_llm_sync(prompt)
        if response:
            result = self._parse_llm_response(response)
            result["document_id"] = document.id
            return result
        
        return {
            "document_id": document.id,
            "main_topic": document.theme,
            "topic_description": "Анализ не выполнен",
            "keywords": [],
            "confidence": 0.0
        }
    
    def generate_summary(self, topic: Dict, documents: List[Document], 
                         start_date: str, end_date: str) -> str:
        """
        Генерация аналитической справки по теме
        """
        # Фильтруем документы по дате
        filtered_docs = []
        for doc in documents:
            if start_date <= doc.date <= end_date:
                filtered_docs.append(doc)
        
        # Подготавливаем сводку документов
        docs_summary = []
        for i, doc in enumerate(filtered_docs[:10], 1):  # Ограничиваем 10 документами
            preview = doc.text[:100] + "..." if len(doc.text) > 100 else doc.text
            docs_summary.append(f"{i}. {doc.date} - {doc.theme}: {preview}")
        
        prompt = self.prompts["summary_generation"].format(
            topic_name=topic.get("topic_name", "Тема"),
            topic_description=topic.get("description", ""),
            start_date=start_date,
            end_date=end_date,
            keywords=", ".join(topic.get("keywords", [])[:5]),
            count=len(filtered_docs),
            documents_summary="\n".join(docs_summary)
        )
        
        response = self._call_llm_sync(prompt)
        if response:
            # Очищаем ответ от лишнего форматирования
            clean_response = re.sub(r'^```(json|markdown)?\s*', '', response, flags=re.MULTILINE)
            clean_response = re.sub(r'\s*```$', '', clean_response, flags=re.MULTILINE)
            return clean_response.strip()
        
        # Фолбэк справка
        return self._generate_fallback_summary(topic, filtered_docs, start_date, end_date)
    
    def _generate_fallback_summary(self, topic: Dict, documents: List[Document],
                                   start_date: str, end_date: str) -> str:
        """Генерация фолбэк справки"""
        summary = f"# Аналитическая справка по теме: {topic.get('topic_name', 'Тема')}\n\n"
        summary += f"## Период анализа: {start_date} - {end_date}\n"
        summary += f"## Количество документов: {len(documents)}\n\n"
        
        summary += "## Основные ключевые слова:\n"
        for keyword in topic.get("keywords", [])[:5]:
            summary += f"- {keyword}\n"
        
        summary += "\n## Распределение по датам:\n"
        dates = [doc.date for doc in documents]
        date_counts = {}
        for date in dates:
            date_counts[date] = date_counts.get(date, 0) + 1
        
        for date, count in sorted(date_counts.items()):
            summary += f"- {date}: {count} документов\n"
        
        summary += "\n## Выводы:\n"
        if len(documents) > 5:
            summary += "Тема активно обсуждалась в указанный период.\n"
        else:
            summary += "Тема обсуждалась ограниченно.\n"
        
        return summary
    
    async def analyze_batch_async(self, documents: List[Document], 
                                  batch_size: int = 5) -> Dict:
        """
        Асинхронный анализ больших пакетов документов
        """
        if len(documents) <= batch_size:
            return self.analyze_topics(documents)
        
        # Разбиваем на батчи
        batches = [documents[i:i + batch_size] for i in range(0, len(documents), batch_size)]
        
        # Анализируем каждый батч
        all_topics = []
        async with aiohttp.ClientSession() as session:
            for i, batch in enumerate(batches):
                print(f"Analyzing batch {i + 1}/{len(batches)}")
                
                formatted_docs = self._prepare_documents_for_prompt(batch)
                prompt = self.prompts["topic_extraction"].format(documents=formatted_docs)
                
                response = await self._call_llm_async(prompt)
                if response:
                    result = self._parse_llm_response(response)
                    if "topics" in result:
                        all_topics.extend(result["topics"])
        
        # Объединяем результаты
        merged_result = self._merge_batch_results(all_topics, documents)
        return merged_result
    
    def _merge_batch_results(self, batch_topics: List[Dict], documents: List[Document]) -> Dict:
        """
        Объединение результатов анализа батчей
        """
        # Простая реализация - берем первые 5-7 тем из всех батчей
        unique_topics = []
        seen_names = set()
        
        for topic in batch_topics:
            name = topic.get("name", "")
            if name and name not in seen_names:
                seen_names.add(name)
                unique_topics.append(topic)
        
        # Ограничиваем количество тем
        unique_topics = unique_topics[:7]
        
        # Распределяем документы по темам
        return self._enrich_analysis_result({"topics": unique_topics}, documents)


# Фабричная функция для создания анализатора
def create_llm_analyzer(
    provider: str = "ollama",
    model: str = "mistral",
    ollama_url: str = "http://localhost:11434"
) -> LLMTopicAnalyzer:
    """
    Создание анализатора с настройками
    """
    provider_enum = LLMProvider(provider.lower())
    return LLMTopicAnalyzer(
        provider=provider_enum,
        model_name=model,
        ollama_url=ollama_url
    )