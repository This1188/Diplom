# urls.py в text_analysis
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TextDocumentViewSet, AnalysisSessionViewSet, TopicAnalysisView, QuickAnalysisView, SummaryReportView

router = DefaultRouter()
router.register(r'documents', TextDocumentViewSet)
router.register(r'analysis-sessions', AnalysisSessionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('analyze-topics/', TopicAnalysisView.as_view(), name='analyze-topics'),
    path('quick-analyze/', QuickAnalysisView.as_view(), name='quick-analyze'),
    path('summary-report/', SummaryReportView.as_view(), name='summary-report'),  # Новый endpoint
]