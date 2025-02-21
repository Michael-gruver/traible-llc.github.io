
# chatbot/views.py

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Document, Conversation, Message
from .services.bedrock_service import BedrockService
from django.conf import settings
import mimetypes

class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({
                'message': 'No file provided'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        file = request.FILES['file']
        content_type = mimetypes.guess_type(file.name)[0]
        
        if content_type != 'application/pdf':
            return Response({
                'message': 'Only PDF files are supported'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Save document
            document = Document.objects.create(
                user=request.user,
                title=file.name,
                file=file,
                content_type=content_type
            )
            
            # Process document
            bedrock = BedrockService()
            if bedrock.process_document(document):
                return Response({
                    'message': 'Document uploaded and processed successfully',
                    'document_id': document.id
                })
            else:
                document.delete()
                return Response({
                    'message': 'Error processing document'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChatView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        conversation_id = request.data.get('conversation_id')
        message = request.data.get('message')
        document_ids = request.data.get('document_ids', [])
        
        if not message:
            return Response({
                'message': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Get or create conversation
            if conversation_id:
                conversation = get_object_or_404(
                    Conversation, 
                    id=conversation_id,
                    user=request.user
                )
            else:
                conversation = Conversation.objects.create(
                    user=request.user,
                    title=message[:50]  # Use first 50 chars as title
                )
            
            # Save user message
            Message.objects.create(
                conversation=conversation,
                content=message,
                role='user'
            )
            
            # Get document context
            bedrock = BedrockService()
            relevant_docs = bedrock.search_documents(message, document_ids)
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            # Get conversation history
            history = Message.objects.filter(
                conversation=conversation
            ).order_by('created_at')[:10]  # Last 10 messages
            
            # Generate response
            response_text = bedrock.get_response(
                message,
                context,
                conversation_history=history
            )
            
            # Save assistant message
            assistant_message = Message.objects.create(
                conversation=conversation,
                content=response_text,
                role='assistant',
                references={
                    'documents': [str(doc_id) for doc_id in document_ids],
                    'contexts': [doc.page_content for doc in relevant_docs]
                }
            )
            
            return Response({
                'conversation_id': conversation.id,
                'message': response_text,
                'references': assistant_message.references
            })
            
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ConversationHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, conversation_id=None):
        try:
            if conversation_id:
                # Get specific conversation
                conversation = get_object_or_404(
                    Conversation,
                    id=conversation_id,
                    user=request.user
                )
                messages = Message.objects.filter(
                    conversation=conversation
                ).order_by('created_at')
                
                return Response({
                    'conversation': {
                        'id': conversation.id,
                        'title': conversation.title,
                        'created_at': conversation.created_at,
                        'messages': [{
                            'id': msg.id,
                            'content': msg.content,
                            'role': msg.role,
                            'created_at': msg.created_at,
                            'references': msg.references
                        } for msg in messages]
                    }
                })
            else:
                # Get all conversations
                conversations = Conversation.objects.filter(
                    user=request.user
                ).order_by('-created_at')
                
                return Response({
                    'conversations': [{
                        'id': conv.id,
                        'title': conv.title,
                        'created_at': conv.created_at,
                        'message_count': conv.message_set.count()
                    } for conv in conversations]
                })
                
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)