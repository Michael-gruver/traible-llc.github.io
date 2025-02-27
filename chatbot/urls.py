from django.urls import path
from .views import *

app_name = 'chatbot'

urlpatterns = [
    path('documents/upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('chat/', ChatView.as_view(), name='chat'),
    path('conversations/', ConversationHistoryView.as_view(), name='conversation-list'),
    path('conversations/<uuid:conversation_id>/', ConversationHistoryView.as_view(), name='conversation-detail'),
]