
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
import magic
class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({
                'message': 'No file provided'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        file = request.FILES['file']
        
        mime = magic.Magic(mime=True)
        content_type = mime.from_buffer(file.read())
        file.seek(0)  # Reset file pointer
        
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

# chatbot/views.py (updated ChatView)

class ChatView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        message = request.data.get('message')
        document_ids = request.data.get('document_ids', [])
        conversation_id = request.data.get('conversation_id')
        
        if not message:
            return Response({
                'message': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if not document_ids:
            return Response({
                'message': 'At least one document ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Verify all documents exist and are processed
            for doc_id in document_ids:
                try:
                    doc = Document.objects.get(id=doc_id, user=request.user)
                    if not doc.is_processed:
                        return Response({
                            'message': f'Document {doc_id} is not processed yet. Please wait and try again.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                except Document.DoesNotExist:
                    return Response({
                        'message': f'Document {doc_id} not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # If conversation_id is provided, check if it exists
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(
                        id=conversation_id,
                        user=request.user
                    )
                    
                    # Get existing document IDs from conversation
                    existing_document_ids = set()
                    for msg in Message.objects.filter(conversation=conversation, role='assistant'):
                        if msg.references and 'documents' in msg.references:
                            existing_document_ids.update(msg.references['documents'])
                    
                    # Check if new documents are being added
                    new_document_ids = set(document_ids) - existing_document_ids
                    if new_document_ids:
                        # Allow new documents to be added to conversation
                        pass  # This is fine - we'll proceed with the existing conversation
                        
                except Conversation.DoesNotExist:
                    return Response({
                        'message': 'Conversation not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                # No conversation_id provided, check for existing conversation with these documents
                # Sort document_ids to ensure consistent lookup
                document_key = '-'.join(sorted(document_ids))
                
                # Look for existing conversation with these exact documents
                conversation = Conversation.objects.filter(
                    user=request.user,
                    document_key=document_key
                ).first()
                
                # If no conversation exists, create a new one
                if not conversation:
                    # Get the first document title to use as conversation title
                    first_doc = Document.objects.get(id=document_ids[0])
                    conversation = Conversation.objects.create(
                        user=request.user,
                        title=first_doc.title[:50],  # Use document name as title
                        document_key=document_key
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
                    'documents': document_ids,
                    'contexts': [doc.page_content for doc in relevant_docs]
                }
            )
            
            return Response({
                'conversation_id': conversation.id,
                'message': response_text,
                'document_ids': document_ids
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