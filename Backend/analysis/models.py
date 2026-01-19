from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Article(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='articles')
    title = models.TextField()
    content = models.TextField()
    raw_text = models.TextField(default='', blank=True)
    publisher = models.CharField(max_length=255, null=True, blank=True) 

class Person(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='persons')
    name = models.CharField(max_length=255)
    confidence_score = models.FloatField(default=0.0)
    
class Keyword(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', 'Положительный'),
        ('negative', 'Отрицательный'),
        ('neutral', 'Нейтральный'),
    ]
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='keywords')
    keyword = models.CharField(max_length=255)
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES)
    frequency = models.IntegerField(default=1)
    relevance_score = models.FloatField(default=0.0)
    
class EventType(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='event_types')
    event_type = models.CharField(max_length=255)
    confidence = models.FloatField(default=0.0)
    
class EventDate(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='dates')
    raw_date = models.CharField(max_length=255)
    parsed_date = models.DateField(null=True, blank=True)
    date_confidence = models.FloatField(default=0.0)