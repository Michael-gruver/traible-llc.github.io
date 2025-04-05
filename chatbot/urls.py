from django.urls import path
from .views import *

app_name = 'chatbot'

urlpatterns = [
    path('documents/upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('chat/', ChatView.as_view(), name='chat'),
    path('conversations/', ConversationHistoryView.as_view(), name='conversation-list'),
    path('conversations/<uuid:conversation_id>/', ConversationHistoryView.as_view(), name='conversation-detail'),
    path('conversations/<uuid:conversation_id>/delete/', ConversationDeleteView.as_view(), name='delete-conversation'),
    path('documents/', UserDocumentsView.as_view(), name='user-documents'),
    path('conversations/initialize/', ConversationInitializeView.as_view(), name='initialize-conversation'),
    path('documents/<int:document_id>/status/', DocumentStatusView.as_view(), name='document_status'),
    path('test-celery/', test_celery, name='test_celery'),
    path('documents/list/', UserDocumentsListView.as_view(), name='user_documents_list'),
    path('documents/<int:document_id>/download/', DocumentDownloadView.as_view(), name='document_download'),
    path('documents/<str:document_id>/delete/', DocumentDeleteView.as_view(), name='document_delete'),
]

