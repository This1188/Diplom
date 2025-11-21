from django.db import models
from django.contrib.postgres.fields import ArrayField

class TextDocument(models.Model):
    """
    Модель для хранения исходных текстовых документов.
    Каждый документ состоит из даты, тематики и текста.
    """
    date = models.DateField(verbose_name='Дата')
    theme = models.CharField(max_length=200, verbose_name='Исходная тематика')
    text = models.TextField(verbose_name='Текст')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Текстовый документ'
        verbose_name_plural = 'Текстовые документы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Документ от {self.date} - {self.theme}"

class AnalysisSession(models.Model):
    """
    Модель для хранения сессий анализа.
    Содержит информацию о когда и какие тексты анализировались.
    """
    name = models.CharField(max_length=200, verbose_name='Название сессии')
    description = models.TextField(blank=True, verbose_name='Описание')
    documents = models.ManyToManyField(TextDocument, verbose_name='Анализируемые документы')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    algorithm_used = models.CharField(max_length=100, default='bayesian', verbose_name='Использованный алгоритм')
    
    class Meta:
        verbose_name = 'Сессия анализа'
        verbose_name_plural = 'Сессии анализа'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Анализ: {self.name}"

class TopicResult(models.Model):
    """
    Модель для хранения результатов тематического анализа.
    Содержит информацию о выявленных темах и количестве документов в каждой теме.
    """
    session = models.ForeignKey(
        AnalysisSession, 
        on_delete=models.CASCADE, 
        related_name='topic_results',
        verbose_name='Сессия анализа'
    )
    topic_name = models.CharField(max_length=200, verbose_name='Название темы')
    topic_keywords = ArrayField(
        models.CharField(max_length=100),
        verbose_name='Ключевые слова темы'
    )
    document_count = models.IntegerField(verbose_name='Количество документов')
    documents = models.ManyToManyField(
        TextDocument, 
        related_name='assigned_topics',
        verbose_name='Документы в теме'
    )
    confidence_score = models.FloatField(verbose_name='Уверенность алгоритма', default=0.0)
    
    class Meta:
        verbose_name = 'Результат тематического анализа'
        verbose_name_plural = 'Результаты тематического анализа'
    
    def __str__(self):
        return f"Тема: {self.topic_name} ({self.document_count} документов)"