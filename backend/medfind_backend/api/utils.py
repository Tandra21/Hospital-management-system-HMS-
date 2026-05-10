# medfind/ai/urls.py
from django.urls import path
from .views import AIChatView, SymptomAnalyzeView, ChatHistoryView, HealthRecordView

urlpatterns = [
    path('chat/',     AIChatView.as_view(),       name='ai-chat'),
    path('symptoms/', SymptomAnalyzeView.as_view(),name='ai-symptoms'),
    path('history/',  ChatHistoryView.as_view(),   name='ai-history'),
    path('health/',   HealthRecordView.as_view(),  name='health-record'),
]
