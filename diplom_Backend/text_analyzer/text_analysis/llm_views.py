from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from .models import TextDocument, AnalysisSession, TopicResult
from .serializers import AnalysisRequestSerializer, TextDocumentUploadSerializer
from .llm_analyzer import create_llm_analyzer, Document
from .llm_config import LLMConfig  # Импортируем конфигурацию
import asyncio

class LLMTopicAnalysisView(APIView):
    """
    View для анализа тем с использованием LLM через Ollama
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Инициализация анализатора с конфигурацией из settings
        self.analyzer = create_llm_analyzer(
            provider=LLMConfig.PROVIDER,
            model=LLMConfig.MODEL_NAME,  # <-- МОДЕЛЬ БЕРЕТСЯ ИЗ КОНФИГУРАЦИИ
            ollama_url=LLMConfig.OLLAMA_URL,
            timeout=LLMConfig.TIMEOUT,
            max_retries=LLMConfig.MAX_RETRIES,
            temperature=LLMConfig.TEMPERATURE
        )
    
    def post(self, request):
        """
        Анализ документов с помощью LLM
        """
        # Можно переопределить модель для конкретного запроса
        custom_model = request.data.get('model_name')
        if custom_model:
            print(f"Using custom model: {custom_model}")
            analyzer = create_llm_analyzer(
                provider=LLMConfig.PROVIDER,
                model=custom_model,
                ollama_url=LLMConfig.OLLAMA_URL
            )
        else:
            analyzer = self.analyzer
        
        serializer = AnalysisRequestSerializer(data=request.data)
        if serializer.is_valid():
            return self.perform_llm_analysis(serializer.validated_data, analyzer)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_llm_analysis(self, validated_data, analyzer):
        """
        Выполнение анализа с использованием LLM
        """
        try:
            with transaction.atomic():
                # Извлекаем данные документов
                documents_data = validated_data['documents']['documents']
                analysis_name = validated_data.get('analysis_name', 'LLM Анализ')
                
                # Сохраняем документы в базу
                text_documents = []
                for doc_data in documents_data:
                    document = TextDocument.objects.create(
                        date=doc_data['date'],
                        theme=doc_data['theme'],
                        text=doc_data['text']
                    )
                    text_documents.append(document)
                
                # Создаем сессию анализа с указанием модели
                session = AnalysisSession.objects.create(
                    name=analysis_name,
                    description=f'Анализ с использованием LLM (Модель: {analyzer.model_name})',
                    algorithm_used=f'llm_{analyzer.model_name}'
                )
                session.documents.set(text_documents)
                
                # Преобразуем в формат для LLM анализатора
                llm_documents = []
                for i, doc in enumerate(text_documents):
                    llm_document = Document(
                        id=f"doc_{i+1}",
                        date=str(doc.date),
                        theme=doc.theme,
                        text=doc.text
                    )
                    llm_documents.append(llm_document)
                
                # Выполняем анализ с LLM
                print(f"Starting LLM analysis for {len(llm_documents)} documents using {analyzer.model_name}...")
                analysis_result = analyzer.analyze_topics(llm_documents)
                
                # Сохраняем результаты в базу
                self.save_llm_results(session, analysis_result, text_documents)
                
                # Формируем ответ
                response_data = self.format_llm_response(session, analysis_result)
                
                return Response(response_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Ошибка при LLM анализе: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def save_llm_results(self, session, analysis_result, text_documents):
        """
        Сохранение результатов LLM анализа
        """
        # Создаем словарь документов для быстрого доступа
        doc_dict = {f"doc_{i+1}": doc for i, doc in enumerate(text_documents)}
        
        for topic_data in analysis_result['topics']:
            # Находим Django документы по их индексам
            topic_documents = []
            for doc_idx in topic_data.get('document_indices', []):
                if doc_idx in doc_dict:
                    topic_documents.append(doc_dict[doc_idx])
                else:
                    # Пытаемся найти по индексу
                    try:
                        idx = int(doc_idx.split('_')[1]) - 1
                        if 0 <= idx < len(text_documents):
                            topic_documents.append(text_documents[idx])
                    except:
                        pass
            
            # Создаем запись результата
            if topic_documents:  # Сохраняем только темы с документами
                topic_result = TopicResult.objects.create(
                    session=session,
                    topic_name=topic_data['topic_name'],
                    topic_keywords=topic_data['keywords'][:10],
                    document_count=len(topic_documents),
                    confidence_score=topic_data.get('confidence', 0.7)
                )
                topic_result.documents.set(topic_documents)
    
    def format_llm_response(self, session, analysis_result):
        """
        Форматирование ответа с LLM результатами
        """
        # Основная статистика по темам
        topic_statistics = []
        for topic_data in analysis_result['topics']:
            if topic_data['document_count'] > 0:
                topic_statistics.append({
                    'topic_id': topic_data['topic_id'],
                    'topic_name': topic_data['topic_name'],
                    'description': topic_data.get('description', ''),
                    'keywords': topic_data['keywords'],
                    'document_count': topic_data['document_count'],
                    'average_confidence': topic_data.get('confidence', 0.7),
                    'document_indices': topic_data.get('document_indices', []),
                    'category': topic_data.get('category', 'general')
                })
        
        # Метаданные анализа
        analysis_metadata = {
            'total_documents': analysis_result['metadata']['total_documents'],
            'topics_discovered': len(topic_statistics),
            'model_used': analysis_result['metadata']['model_used'],
            'provider': analysis_result['metadata']['provider'],
            'processing_time': analysis_result['metadata']['timestamp']
        }
        
        return {
            'session_id': session.id,
            'session_name': session.name,
            'topic_statistics': topic_statistics,
            'analysis_metadata': analysis_metadata
        }


class LLMSummaryView(APIView):
    """
    View для генерации аналитической справки с помощью LLM
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.analyzer = create_llm_analyzer()
    
    def post(self, request):
        """
        Генерация справки по теме с использованием LLM
        """
        try:
            session_id = request.data.get('session_id')
            topic_name = request.data.get('topic_name')
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            
            if not all([session_id, topic_name, start_date, end_date]):
                return Response(
                    {'error': 'Необходимы session_id, topic_name, start_date и end_date'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Получаем сессию и тему
            session = AnalysisSession.objects.get(id=session_id)
            topic_result = session.topic_results.filter(topic_name=topic_name).first()
            
            if not topic_result:
                return Response(
                    {'error': 'Тема не найдена в указанной сессии'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Получаем документы темы
            topic_documents = topic_result.documents.all()
            
            # Фильтруем по дате
            filtered_documents = topic_documents.filter(
                date__range=[start_date, end_date]
            )
            
            # Преобразуем в формат для LLM
            llm_documents = []
            for i, doc in enumerate(filtered_documents):
                llm_doc = Document(
                    id=f"doc_{i+1}",
                    date=str(doc.date),
                    theme=doc.theme,
                    text=doc.text
                )
                llm_documents.append(llm_doc)
            
            # Подготавливаем данные темы
            topic_data = {
                'topic_name': topic_result.topic_name,
                'description': f'Тема из анализа сессии "{session.name}"',
                'keywords': topic_result.topic_keywords
            }
            
            # Генерируем справку с LLM
            print(f"Generating LLM summary for topic: {topic_name}")
            summary = self.analyzer.generate_summary(
                topic=topic_data,
                documents=llm_documents,
                start_date=start_date,
                end_date=end_date
            )
            
            return Response({
                'topic_name': topic_name,
                'period': f'{start_date} - {end_date}',
                'documents_analyzed': len(filtered_documents),
                'summary': summary,
                'generated_at': str(datetime.now())
            })
            
        except AnalysisSession.DoesNotExist:
            return Response(
                {'error': 'Сессия анализа не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Ошибка при генерации справки: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LLMQuickAnalysisView(APIView):
    """
    Быстрый анализ без сохранения в базу
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.analyzer = create_llm_analyzer()
    
    def post(self, request):
        """
        Быстрый анализ текстов с LLM
        """
        serializer = TextDocumentUploadSerializer(data=request.data)
        if serializer.is_valid():
            try:
                documents_data = serializer.validated_data['documents']
                
                # Преобразуем в формат для LLM
                llm_documents = []
                for i, doc_data in enumerate(documents_data):
                    llm_doc = Document(
                        id=f"doc_{i+1}",
                        date=doc_data['date'],
                        theme=doc_data['theme'],
                        text=doc_data['text']
                    )
                    llm_documents.append(llm_doc)
                
                # Выполняем анализ
                print(f"Quick LLM analysis for {len(llm_documents)} documents")
                analysis_result = self.analyzer.analyze_topics(llm_documents)
                
                # Форматируем результат
                topic_statistics = []
                for topic_data in analysis_result['topics']:
                    if topic_data['document_count'] > 0:
                        topic_statistics.append({
                            'topic_name': topic_data['topic_name'],
                            'description': topic_data.get('description', ''),
                            'keywords': topic_data['keywords'],
                            'document_count': topic_data['document_count'],
                            'confidence': topic_data.get('confidence', 0.7)
                        })
                
                return Response({
                    'topic_statistics': topic_statistics,
                    'total_documents_analyzed': len(llm_documents),
                    'model_used': analysis_result['metadata']['model_used']
                })
                
            except Exception as e:
                return Response(
                    {'error': f'Ошибка быстрого анализа: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)