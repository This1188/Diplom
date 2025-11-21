from django.contrib import admin
from .models import TextDocument, AnalysisSession, TopicResult

class TextDocumentAdmin(admin.ModelAdmin):
    list_display = ['date', 'theme', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['theme', 'text']
    readonly_fields = ['created_at']

class TopicResultInline(admin.TabularInline):
    model = TopicResult
    extra = 0
    readonly_fields = ['topic_name', 'document_count', 'confidence_score']

class AnalysisSessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'algorithm_used']
    list_filter = ['created_at', 'algorithm_used']
    search_fields = ['name', 'description']
    inlines = [TopicResultInline]
    readonly_fields = ['created_at']

class TopicResultAdmin(admin.ModelAdmin):
    list_display = ['topic_name', 'session', 'document_count', 'confidence_score']
    list_filter = ['session', 'confidence_score']
    search_fields = ['topic_name', 'topic_keywords']

admin.site.register(TextDocument, TextDocumentAdmin)
admin.site.register(AnalysisSession, AnalysisSessionAdmin)
admin.site.register(TopicResult, TopicResultAdmin)