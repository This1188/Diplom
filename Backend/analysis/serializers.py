from rest_framework import serializers
from .models import Document, Article, Person, Keyword, EventType, EventDate


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['name', 'confidence_score']


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ['keyword', 'sentiment', 'frequency', 'relevance_score']


class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = ['event_type', 'confidence']


class EventDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventDate
        fields = ['raw_date', 'parsed_date', 'date_confidence']


class ArticleSerializer(serializers.ModelSerializer):
    persons = PersonSerializer(many=True, read_only=True)
    keywords = KeywordSerializer(many=True, read_only=True)
    event_types = EventTypeSerializer(many=True, read_only=True)
    dates = EventDateSerializer(many=True, read_only=True)
    
    sentiment = serializers.SerializerMethodField()
    event_categories = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'raw_text', 'publisher',
            'persons', 'keywords', 'event_types', 'dates',
            'sentiment', 'event_categories', 'metadata'
        ]
    
    def get_sentiment(self, obj):
        """Вычисляет тональность статьи на основе ключевых слов"""
        keywords = obj.keywords.all()
        
        if not keywords:
            return {
                'overall': 'neutral',
                'confidence': 0.5
            }
        
        sentiment_counts = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }
        
        for kw in keywords:
            sentiment_counts[kw.sentiment] = sentiment_counts.get(kw.sentiment, 0) + 1
        
        total = len(keywords)
        if total == 0:
            return {
                'overall': 'neutral',
                'confidence': 0.5
            }
        
        max_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])
        confidence = max_sentiment[1] / total
        
        return {
            'overall': max_sentiment[0],
            'confidence': round(confidence, 2),
            'counts': sentiment_counts,
            'percentages': {
                sent: round(count / total * 100, 1)
                for sent, count in sentiment_counts.items()
            }
        }
    
    def get_event_categories(self, obj):
        """Возвращает категории событий"""
        event_types = obj.event_types.all()
        
        if not event_types:
            return []
        
        return [
            {
                'event_type': et.event_type,
                'confidence': et.confidence
            }
            for et in event_types
        ]
    
    def get_metadata(self, obj):
        """Возвращает метаданные статьи"""
        word_count = len(obj.content.split()) if obj.content else 0
        char_count = len(obj.content) if obj.content else 0
        
        return {
            'word_count': word_count,
            'char_count': char_count,
            'persons_count': obj.persons.count(),
            'keywords_count': obj.keywords.count(),
            'publisher': obj.publisher
        }


class DocumentSerializer(serializers.ModelSerializer):
    articles = ArticleSerializer(many=True, read_only=True)
    
    statistics = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'uploaded_at', 'articles', 'statistics']
    
    def get_statistics(self, obj):
        """Вычисляет статистику документа"""
        articles = obj.articles.all()
        total_articles = articles.count()
        
        if total_articles == 0:
            return {}
        
        total_persons = sum(article.persons.count() for article in articles)
        total_keywords = sum(article.keywords.count() for article in articles)
        
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for article in articles:
            keywords = article.keywords.all()
            for kw in keywords:
                sentiment_counts[kw.sentiment] = sentiment_counts.get(kw.sentiment, 0) + 1
        
        event_type_counts = {}
        for article in articles:
            event_types = article.event_types.all()
            for et in event_types:
                event_type_counts[et.event_type] = event_type_counts.get(et.event_type, 0) + 1
        
        return {
            'total_articles': total_articles,
            'total_persons': total_persons,
            'total_keywords': total_keywords,
            'sentiment_distribution': sentiment_counts,
            'event_type_distribution': event_type_counts,
            'averages': {
                'persons_per_article': round(total_persons / total_articles, 1),
                'keywords_per_article': round(total_keywords / total_articles, 1)
            }
        }