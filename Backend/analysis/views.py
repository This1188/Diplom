import os
import tempfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .parsers import DocumentParser, TextAnalyzer
from .models import Document, Article, Person, Keyword, EventType, EventDate
import docx
from docx2txt import process
import traceback


class AnalyzeDocumentView(APIView):
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        file_extension = os.path.splitext(file.name)[1].lower()
        
        print(f"Получен файл: {file.name}, расширение: {file_extension}, размер: {file.size} байт")
        
        try:
            content = ""
            
            if file_extension == '.txt':
                content = file.read().decode('utf-8', errors='ignore')
            
            elif file_extension in ['.docx', '.doc']:
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                    for chunk in file.chunks():
                        tmp_file.write(chunk)
                    tmp_file_path = tmp_file.name
                
                try:
                    if file_extension == '.docx':
                        doc = docx.Document(tmp_file_path)
                        content = "\n".join([para.text for para in doc.paragraphs])
                    else:
                        content = process(tmp_file_path)
                finally:
                    os.unlink(tmp_file_path)
            
            else:
                return Response(
                    {'error': f'Неподдерживаемый формат файла: {file_extension}. Поддерживаются: .txt, .doc, .docx'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            print(f"Файл прочитан, размер текста: {len(content)} символов")
            
        except Exception as e:
            print(f"Ошибка чтения файла: {e}")
            traceback.print_exc()
            return Response(
                {'error': f'Ошибка обработки файла: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        document = Document.objects.create(title=file.name)
        print(f"Создан документ с ID: {document.id}")
        
        parser = DocumentParser()
        articles_data = parser.parse(content)
        
        print(f"Парсер нашел {len(articles_data)} статей")
        
        if len(articles_data) == 0:
            print("Парсер не нашел статьи!")
            return Response({'error': 'Не удалось извлечь статьи из документа'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        analyzer = TextAnalyzer()
        results = []
        
        for idx, article_data in enumerate(articles_data):
            try:
                text = article_data['content']
                title = article_data['title']
                
                #print(f"Анализируем статью {idx+1}: {title[:50]}...")
                
                analyzed = analyzer.analyze_article(article_data)
                
                article = Article.objects.create(
                    document=document,
                    title=title[:1000],
                    content=analyzed['clean_text'][:2000],
                    raw_text=text
                )
                
                for person_name in analyzed['persons']:
                    Person.objects.create(
                        article=article,
                        name=person_name[:255],
                        confidence_score=0.8
                    )
                
                for kw in analyzed['keywords']:
                    Keyword.objects.create(
                        article=article,
                        keyword=kw['keyword'][:255],
                        sentiment=kw['sentiment'],
                        frequency=kw.get('frequency', 1),
                        relevance_score=kw.get('score', 0.0)
                    )
                
                EventType.objects.create(
                    article=article,
                    event_type=analyzed['event_type'][:255],
                    confidence=0.7
                )
                
                EventDate.objects.create(
                    article=article,
                    raw_date=analyzed['date']['raw'][:255],
                    parsed_date=analyzed['date']['parsed'],
                    date_confidence=0.6
                )
                
                results.append({
                    'id': article.id,
                    'title': article.title,
                    'content': article.content[:500] + '...' if len(article.content) > 500 else article.content,
                    'raw_text': text[:1000] + '...' if len(text) > 1000 else text,
                    'persons': analyzed['persons'],
                    'keywords': analyzed['keywords'],
                    'event_type': analyzed['event_type'],
                    'date': analyzed['date']['raw'],
                    'date_parsed': analyzed['date']['parsed'],
                    'publisher': analyzed.get('publisher'),
                    'word_count': analyzed['metadata']['word_count'],
                    'char_count': analyzed['metadata']['char_count']
                })
                
                #print(f"Статья {idx+1} проанализирована: {len(analyzed['persons'])} персон, {len(analyzed['keywords'])} ключевых слов")
                #print(f"Дата: {analyzed['date']['raw']}, Тип события: {analyzed['event_type']}")
                
            except Exception as e:
                print(f"Ошибка при анализе статьи {idx+1}: {e}")
                traceback.print_exc()
                continue
        
        print(f"Анализ завершен. Обработано статей: {len(results)}")
        
        # Статистика
        event_types = {}
        sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for article in results:
            event_type = article['event_type']
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
            for keyword in article.get('keywords', []):
                sentiment = keyword.get('sentiment', 'neutral')
                sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
        
        return Response({
            'document_id': document.id,
            'document_title': file.name,
            'articles_count': len(results),
            'articles': results,
            'statistics': {
                'total_articles': len(results),
                'event_types_distribution': event_types,
                'sentiments_distribution': sentiments,
                'total_persons': sum(len(a['persons']) for a in results),
                'total_keywords': sum(len(a['keywords']) for a in results)
            }
        })