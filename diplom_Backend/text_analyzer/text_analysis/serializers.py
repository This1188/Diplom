from rest_framework import serializers
from .models import TextDocument, AnalysisSession, TopicResult

class TextDocumentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для текстовых документов.
    Преобразует объекты TextDocument в JSON и обратно.
    """
    class Meta:
        model = TextDocument
        fields = ['id', 'date', 'theme', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']

class TextDocumentUploadSerializer(serializers.Serializer):
    """
    Сериализатор для загрузки текстовых документов.
    Поддерживает различные форматы ввода.
    """
    documents = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        ),
        help_text="Список документов в формате: [{'date': '...', 'theme': '...', 'text': '...'}]"
    )
    
    def validate_documents(self, value):
        """
        Валидация структуры загружаемых документов.
        """
        for doc in value:
            if 'date' not in doc or 'theme' not in doc or 'text' not in doc:
                raise serializers.ValidationError(
                    "Каждый документ должен содержать поля: date, theme, text"
                )
        return value

class AnalysisSessionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для сессий анализа.
    """
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalysisSession
        fields = ['id', 'name', 'description', 'document_count', 'created_at', 'algorithm_used']
        read_only_fields = ['id', 'created_at']
    
    def get_document_count(self, obj):
        return obj.documents.count()

class TopicResultSerializer(serializers.ModelSerializer):
    """
    Сериализатор для результатов тематического анализа.
    """
    session_name = serializers.CharField(source='session.name', read_only=True)
    
    class Meta:
        model = TopicResult
        fields = [
            'id', 'session', 'session_name', 'topic_name', 
            'topic_keywords', 'document_count', 'confidence_score'
        ]
        read_only_fields = ['id']

class AnalysisRequestSerializer(serializers.Serializer):
    """
    Сериализатор для запроса анализа текстов.
    """
    documents = TextDocumentUploadSerializer()
    analysis_name = serializers.CharField(max_length=200, required=False)
    analysis_description = serializers.CharField(required=False)
    num_topics = serializers.IntegerField(default=5, min_value=2, max_value=20)
    auto_determine_topics = serializers.BooleanField(default=False)
    
    class Meta:
        fields = ['documents', 'analysis_name', 'analysis_description', 'num_topics', 'auto_determine_topics']

class AnalysisResultSerializer(serializers.Serializer):
    """
    Сериализатор для возврата результатов анализа.
    """
    session_id = serializers.IntegerField()
    session_name = serializers.CharField()
    topic_statistics = serializers.ListField(
        child=serializers.DictField()
    )
    analysis_metadata = serializers.DictField()
    
    class Meta:
        fields = ['session_id', 'session_name', 'topic_statistics', 'analysis_metadata']