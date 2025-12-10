from rest_framework import viewsets, status
from django.db.models import Q
from datetime import datetime
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from .models import TextDocument, AnalysisSession, TopicResult
from .serializers import (
    TextDocumentSerializer, AnalysisSessionSerializer,
    TopicResultSerializer, AnalysisRequestSerializer,
    AnalysisResultSerializer, TextDocumentUploadSerializer
)
from .bayesian_analyzer import BayesianTopicAnalyzer, EnhancedBayesianAnalyzer


# Добавьте импорт в начале файла
from .improved_analyzer import create_analyzer, HybridTopicAnalyzer
from .training_data import TopicTrainingData

class ImprovedTopicAnalysisView(APIView):
    """
    Улучшенный API для тематического анализа
    """
    
    def post(self, request):
        """
        Основной endpoint для анализа с улучшенным алгоритмом
        """
        serializer = AnalysisRequestSerializer(data=request.data)
        if serializer.is_valid():
            return self.perform_enhanced_analysis(serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_enhanced_analysis(self, validated_data):
        """
        Выполнение улучшенного анализа
        """
        try:
            with transaction.atomic():
                # Извлекаем данные
                documents_data = validated_data['documents']['documents']
                analysis_name = validated_data.get('analysis_name', 'Улучшенный анализ')
                use_advanced = validated_data.get('use_advanced', True)
                
                # Сохраняем документы
                text_documents = []
                for doc_data in documents_data:
                    document = TextDocument.objects.create(
                        date=doc_data['date'],
                        theme=doc_data['theme'],
                        text=doc_data['text']
                    )
                    text_documents.append(document)
                
                # Создаем сессию
                session = AnalysisSession.objects.create(
                    name=analysis_name,
                    description='Анализ с улучшенным алгоритмом'
                )
                session.documents.set(text_documents)
                
                # Выбираем анализатор
                if use_advanced:
                    # Используем гибридный анализатор
                    analyzer = create_analyzer(mode='hybrid')
                    
                    # Извлекаем тексты
                    texts = [doc.text for doc in text_documents]
                    
                    # Загружаем обучающие данные для дообучения
                    training_data = TopicTrainingData()
                    if len(training_data.data) > 0:
                        print(f"Используем {len(training_data.data)} обучающих примеров")
                    
                    # Выполняем анализ
                    analysis_result = analyzer.ensemble_analysis(texts)
                    
                    # Используем консенсусные результаты
                    topic_stats = analysis_result['consensus']['topic_statistics']
                    
                else:
                    # Используем старый анализатор для обратной совместимости
                    from .bayesian_analyzer import EnhancedBayesianAnalyzer
                    analyzer = EnhancedBayesianAnalyzer()
                    texts = [doc.text for doc in text_documents]
                    result = analyzer.analyze_with_auto_topics(texts)
                    topic_stats = result['topic_statistics']
                
                # Сохраняем результаты
                self.save_enhanced_results(session, topic_stats, text_documents)
                
                # Формируем улучшенный ответ
                response_data = self.format_enhanced_response(session, topic_stats, text_documents)
                
                return Response(response_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {'error': f'Ошибка при анализе: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def save_enhanced_results(self, session, topic_stats, text_documents):
        """
        Сохранение улучшенных результатов анализа
        """
        for topic_stat in topic_stats:
            if topic_stat['document_count'] > 0:
                # Находим документы для этой темы
                topic_docs_indices = topic_stat['document_indices']
                topic_documents = [text_documents[i] for i in topic_docs_indices]
                
                # Создаем запись результата
                topic_result = TopicResult.objects.create(
                    session=session,
                    topic_name=topic_stat['topic_name'],
                    topic_keywords=topic_stat['keywords'][:10],  # Сохраняем топ-10 ключевых слов
                    document_count=topic_stat['document_count'],
                    confidence_score=topic_stat['average_confidence']
                )
                topic_result.documents.set(topic_documents)
    
    def format_enhanced_response(self, session, topic_stats, text_documents):
        """
        Форматирование улучшенного ответа
        """
        formatted_stats = []
        for topic_stat in topic_stats:
            if topic_stat['document_count'] > 0:
                # Форматируем информацию о теме
                formatted_topic = {
                    'topic_id': topic_stat['topic_id'],
                    'topic_name': topic_stat['topic_name'],
                    'theme_guess': topic_stat.get('theme_guess', 'неизвестно'),
                    'keywords': topic_stat['keywords'],
                    'document_count': topic_stat['document_count'],
                    'average_confidence': topic_stat['average_confidence'],
                    'document_indices': topic_stat['document_indices'],
                    'sample_documents': []
                }
                
                # Добавляем примеры документов
                for idx in topic_stat['document_indices'][:3]:  # Первые 3 документа
                    if idx < len(text_documents):
                        doc = text_documents[idx]
                        formatted_topic['sample_documents'].append({
                            'date': doc.date,
                            'theme': doc.theme,
                            'text_preview': doc.text[:100] + '...' if len(doc.text) > 100 else doc.text
                        })
                
                formatted_stats.append(formatted_topic)
        
        # Метаданные анализа
        analysis_metadata = {
            'total_documents': len(text_documents),
            'topics_discovered': len([t for t in topic_stats if t['document_count'] > 0]),
            'algorithm_used': 'Hybrid LDA+NMF',
            'model_version': '1.0'
        }
        
        return {
            'session_id': session.id,
            'session_name': session.name,
            'topic_statistics': formatted_stats,
            'analysis_metadata': analysis_metadata
        }


# Добавьте новый endpoint в urls.py
path('enhanced-analyze-topics/', ImprovedTopicAnalysisView.as_view(), name='enhanced-analyze-topics'),

class SummaryReportView(APIView):
    """
    View для получения справки по временному диапазону
    """
    
    def post(self, request):
        try:
            session_id = request.data.get('session_id')
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            
            if not all([session_id, start_date, end_date]):
                return Response(
                    {'error': 'Необходимы session_id, start_date и end_date'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Конвертируем даты
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Получаем сессию
            session = AnalysisSession.objects.get(id=session_id)
            
            # Фильтруем документы по дате
            filtered_documents = session.documents.filter(
                date__range=[start_date, end_date]
            )
            
            # Получаем темы для отфильтрованных документов
            topic_results = TopicResult.objects.filter(
                session=session,
                documents__in=filtered_documents
            ).distinct()
            
            # Формируем статистику
            summary_data = self.generate_summary(
                topic_results, filtered_documents, start_date, end_date
            )
            
            return Response(summary_data)
            
        except AnalysisSession.DoesNotExist:
            return Response(
                {'error': 'Сессия анализа не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Ошибка при формировании справки: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def generate_summary(self, topic_results, documents, start_date, end_date):
        """
        Генерация сводной справки
        """
        total_documents = documents.count()
        
        topic_stats = []
        for topic in topic_results:
            topic_docs = topic.documents.filter(id__in=documents.values_list('id', flat=True))
            topic_stats.append({
                'topic_name': topic.topic_name,
                'document_count': topic_docs.count(),
                'keywords': topic.topic_keywords,
                'confidence_score': topic.confidence_score,
                'percentage': round((topic_docs.count() / total_documents) * 100, 2) if total_documents > 0 else 0
            })
        
        return {
            'summary_period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'total_documents': total_documents
            },
            'topic_statistics': topic_stats,
            'dominant_topic': max(topic_stats, key=lambda x: x['document_count']) if topic_stats else None
        }

class TextDocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления текстовыми документами.
    Предоставляет CRUD операции для документов.
    """
    queryset = TextDocument.objects.all()
    serializer_class = TextDocumentSerializer
    
    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """
        Массовая загрузка текстовых документов.
        """
        serializer = TextDocumentUploadSerializer(data=request.data)
        if serializer.is_valid():
            documents_data = serializer.validated_data['documents']
            
            created_documents = []
            for doc_data in documents_data:
                document = TextDocument.objects.create(
                    date=doc_data['date'],
                    theme=doc_data['theme'],
                    text=doc_data['text']
                )
                created_documents.append(document)
            
            result_serializer = TextDocumentSerializer(created_documents, many=True)
            return Response({
                'message': f'Успешно загружено {len(created_documents)} документов',
                'documents': result_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AnalysisSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления сессиями анализа.
    """
    queryset = AnalysisSession.objects.all()
    serializer_class = AnalysisSessionSerializer
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """
        Получение результатов конкретной сессии анализа.
        """
        session = self.get_object()
        topic_results = session.topic_results.all()
        serializer = TopicResultSerializer(topic_results, many=True)
        return Response(serializer.data)

class TopicAnalysisView(APIView):
    """
    Основное API view для проведения тематического анализа.
    """
    
    def post(self, request):
        """
        Основной endpoint для анализа текстов.
        Принимает документы и возвращает результаты тематического анализа.
        """
        serializer = AnalysisRequestSerializer(data=request.data)
        if serializer.is_valid():
            return self.perform_analysis(serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_analysis(self, validated_data):
        """
        Выполнение тематического анализа с использованием алгоритма Байеса.
        """
        try:
            with transaction.atomic():
                # Извлекаем данные документов
                documents_data = validated_data['documents']['documents']
                analysis_name = validated_data.get('analysis_name', 'Анализ текстов')
                analysis_description = validated_data.get('analysis_description', '')
                num_topics = validated_data['num_topics']
                auto_determine = validated_data['auto_determine_topics']
                
                # Сохраняем документы в базу
                text_documents = []
                for doc_data in documents_data:
                    document = TextDocument.objects.create(
                        date=doc_data['date'],
                        theme=doc_data['theme'],
                        text=doc_data['text']
                    )
                    text_documents.append(document)
                
                # Создаем сессию анализа
                session = AnalysisSession.objects.create(
                    name=analysis_name,
                    description=analysis_description
                )
                session.documents.set(text_documents)
                
                # Подготавливаем тексты для анализа
                texts = [doc.text for doc in text_documents]
                
                # Выбираем анализатор
                if auto_determine:
                    analyzer = EnhancedBayesianAnalyzer()
                    analysis_result = analyzer.analyze_with_auto_topics(texts)
                else:
                    analyzer = BayesianTopicAnalyzer(n_topics=num_topics)
                    analysis_result = analyzer.analyze_topics(texts)
                
                # Сохраняем результаты в базу
                self.save_analysis_results(session, analysis_result, text_documents)
                
                # Формируем ответ
                response_data = self.format_analysis_response(session, analysis_result)
                
                return Response(response_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {'error': f'Ошибка при анализе: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def save_analysis_results(self, session, analysis_result, text_documents):
        """
        Сохранение результатов анализа в базу данных.
        """
        for topic_stat in analysis_result['topic_statistics']:
            # Находим документы для этой темы
            topic_docs_indices = topic_stat['document_indices']
            topic_documents = [text_documents[i] for i in topic_docs_indices]
            
            # Создаем запись результата
            topic_result = TopicResult.objects.create(
                session=session,
                topic_name=topic_stat['topic_name'],
                topic_keywords=topic_stat['keywords'],
                document_count=topic_stat['document_count'],
                confidence_score=topic_stat['average_confidence']
            )
            topic_result.documents.set(topic_documents)
    
    def format_analysis_response(self, session, analysis_result):
        """
        Форматирование ответа с результатами анализа.
        """
        # Основная статистика по темам (то что требуется в задании)
        topic_statistics = []
        for topic_stat in analysis_result['topic_statistics']:
            topic_statistics.append({
                'topic_name': topic_stat['topic_name'],
                'document_count': topic_stat['document_count'],
                'keywords': topic_stat['keywords'],
                'average_confidence': topic_stat['average_confidence'],
                'document_indices': topic_stat.get('document_indices', [])  # Добавлено
            })
        
        # Метаданные анализа
        analysis_metadata = {
            'total_documents': len(analysis_result['document_assignments']),
            'topics_discovered': len(analysis_result['topic_statistics']),
            'algorithm_used': 'Bayesian LDA',
            'processing_time': 'реальное время можно добавить при необходимости'
        }
        
        return {
            'session_id': session.id,
            'session_name': session.name,
            'topic_statistics': topic_statistics,
            'analysis_metadata': analysis_metadata
        }

class QuickAnalysisView(APIView):
    """
    View для быстрого анализа без сохранения в базу.
    """
    
    def post(self, request):
        """
        Быстрый анализ текстов без сохранения в базу.
        Возвращает только результаты анализа.
        """
        serializer = TextDocumentUploadSerializer(data=request.data)
        if serializer.is_valid():
            try:
                documents_data = serializer.validated_data['documents']
                texts = [doc['text'] for doc in documents_data]
                
                # Быстрый анализ с автоматическим определением тем
                analyzer = EnhancedBayesianAnalyzer()
                analysis_result = analyzer.analyze_with_auto_topics(texts)
                
                # Форматируем ответ
                topic_statistics = []
                for topic_stat in analysis_result['topic_statistics']:
                    topic_statistics.append({
                        'topic_name': topic_stat['topic_name'],
                        'document_count': topic_stat['document_count'],
                        'keywords': topic_stat['keywords'],
                        'average_confidence': topic_stat['average_confidence']
                    })
                
                return Response({
                    'topic_statistics': topic_statistics,
                    'total_documents_analyzed': len(texts),
                    'topics_discovered': len(topic_statistics)
                })
                
            except Exception as e:
                return Response(
                    {'error': f'Ошибка анализа: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)