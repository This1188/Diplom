from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TextDocumentViewSet, AnalysisSessionViewSet, TopicAnalysisView, QuickAnalysisView
from .llm_views import LLMTopicAnalysisView, LLMSummaryView, LLMQuickAnalysisView

router = DefaultRouter()
router.register(r'documents', TextDocumentViewSet)
router.register(r'analysis-sessions', AnalysisSessionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('analyze-topics/', TopicAnalysisView.as_view(), name='analyze-topics'),
    path('quick-analyze/', QuickAnalysisView.as_view(), name='quick-analyze'),
    
    # Новые LLM endpoints
    path('llm/analyze-topics/', LLMTopicAnalysisView.as_view(), name='llm-analyze-topics'),
    path('llm/generate-summary/', LLMSummaryView.as_view(), name='llm-generate-summary'),
    path('llm/quick-analyze/', LLMQuickAnalysisView.as_view(), name='llm-quick-analyze'),
]