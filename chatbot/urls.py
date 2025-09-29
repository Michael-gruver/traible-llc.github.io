from django.urls import path
from .views import *
from .health_views import HealthCheckView, DetailedHealthView, MetricsView, ReadinessView, LivenessView

app_name = 'chatbot'

urlpatterns = [
    # Document endpoints
    path('documents/upload/', DocumentUploadView.as_view(), name='upload-document'),
    path('documents/', UserDocumentsView.as_view(), name='user-documents'),
    path('documents/list/', UserDocumentsListView.as_view(), name='user_documents_list'),
    path('documents/<int:document_id>/status/', DocumentStatusView.as_view(), name='document_status'),
    path('documents/<int:document_id>/download/', DocumentDownloadView.as_view(), name='document_download'),
    path('documents/<str:document_id>/delete/', DocumentDeleteView.as_view(), name='document_delete'),
    
    # Chat endpoints
    path('chat/', ChatView.as_view(), name='chat'),
    
    # Conversation endpoints
    path('conversations/', ConversationHistoryView.as_view(), name='conversation-list'),
    path('conversations/<uuid:conversation_id>/', ConversationHistoryView.as_view(), name='conversation-detail'),
    path('conversations/<uuid:conversation_id>/delete/', ConversationDeleteView.as_view(), name='delete-conversation'),
    path('conversations/initialize/', ConversationInitializeView.as_view(), name='initialize-conversation'),
    
    # Health and monitoring endpoints
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('health/detailed/', DetailedHealthView.as_view(), name='detailed-health'),
    path('metrics/', MetricsView.as_view(), name='metrics'),
    path('readiness/', ReadinessView.as_view(), name='readiness'),
    path('liveness/', LivenessView.as_view(), name='liveness'),
    
    # Development endpoints
    path('test-celery/', test_celery, name='test_celery'),
]

