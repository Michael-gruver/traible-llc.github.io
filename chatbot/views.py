# chatbot/views.py
from django.http import StreamingHttpResponse
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
import json
from django.db import models

class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        conversation_id = request.data.get('conversation_id')  # Add this to accept a conversation ID
        
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
                # If conversation_id provided, add document to that conversation
                if conversation_id:
                    try:
                        conversation = Conversation.objects.get(
                            id=conversation_id,
                            user=request.user
                        )
                        
                        # Add system message to record document upload
                        Message.objects.create(
                            conversation=conversation,
                            content=f"Document uploaded: {document.title}",
                            role='system',
                            references={
                                'documents': [str(document.id)],
                                'contexts': [],
                                'event_type': 'document_upload'
                            }
                        )
                        
                        return Response({
                            'message': 'Document uploaded and added to conversation successfully',
                            'document_id': document.id,
                            'conversation_id': conversation.id
                        })
                        
                    except Conversation.DoesNotExist:
                        return Response({
                            'message': 'Conversation not found'
                        }, status=status.HTTP_404_NOT_FOUND)
                
                # Create new conversation if no conversation_id provided
                else:
                    document_key = document.id
                    conversation = Conversation.objects.create(
                        user=request.user,
                        title=document.title[:50],
                        document_key=document_key
                    )
                    
                    # Add system message to record document upload
                    Message.objects.create(
                        conversation=conversation,
                        content=f"Document uploaded: {document.title}",
                        role='system',
                        references={
                            'documents': [str(document.id)],
                            'contexts': [],
                            'event_type': 'document_upload'
                        }
                    )
                    
                    # Add greeting message for new conversations
                    greeting_message = Message.objects.create(
                        conversation=conversation,
                        content="How can I assist you with this document today?",
                        role='assistant',
                        references={
                            'documents': [str(document.id)],
                            'contexts': []
                        }
                    )
                    
                    return Response({
                        'message': 'Document uploaded and processed successfully',
                        'document_id': document.id,
                        'conversation_id': conversation.id,
                        'greeting': greeting_message.content
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
    
    def stream_response(self, bedrock, message, context, history, conversation, document_ids):
        """Stream the response from Claude and save the complete response when done"""
        full_response = ""
        
        # Create a generator that yields each piece of the response
        def response_generator():
            nonlocal full_response
            
            yield "data: {\"type\": \"start\"}\n\n"
            
            # Use the streaming response method
            response_generator = bedrock.get_response(message, context, history, stream=True)
            for text_chunk in response_generator:
                if text_chunk:
                    # Format for EventSource
                    chunk_data = json.dumps({
                        "type": "chunk",
                        "text": text_chunk
                    })
                    yield f"data: {chunk_data}\n\n"
                    full_response += text_chunk
            
            # Send a completion message
            yield "data: {\"type\": \"end\"}\n\n"
            
            # Save the message to the database after completion
            Message.objects.create(
                conversation=conversation,
                content=full_response,
                role='assistant',
                references={
                    'documents': document_ids,
                    'contexts': [context]
                }
            )
            
        return response_generator()
    
    def post(self, request):
        message = request.data.get('message')
        document_ids = request.data.get('document_ids', [])
        conversation_id = request.data.get('conversation_id')
        stream_mode = request.data.get('stream', False)  # Optional streaming parameter
        
        print(f"DEBUG: Received request - message: {message}, document_ids: {document_ids}, stream: {stream_mode}")
        
        if not message:
            return Response({
                'message': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if not document_ids:
            return Response({
                'message': 'At least one document ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            print("hereeeeee")
            # Verify all documents exist and are processed
            accessible_docs = Document.objects.filter(
                models.Q(user=request.user)  # Documents owned by the user
            ).distinct()
            print(accessible_docs)
            for doc_id in document_ids:
                try:
                    doc = accessible_docs.filter(id=doc_id).first()
                    
                    if not doc:
                        return Response({
                            'message': f'Document {doc_id} not found or you do not have access to it'
                        }, status=status.HTTP_404_NOT_FOUND)
                        
                    if not doc.is_processed:
                        return Response({
                            'message': f'Document {doc_id} is not processed yet. Please wait and try again.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                except Document.DoesNotExist:
                    return Response({
                        'message': f'Document {doc_id} not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Get or create conversation
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(
                        id=conversation_id,
                        user=request.user
                    )
                except Conversation.DoesNotExist:
                    return Response({
                        'message': 'Conversation not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                # No conversation_id provided, check if one was already created
                document_key = '-'.join(sorted(document_ids))
                conversation = Conversation.objects.filter(
                    user=request.user,
                    document_key=document_key
                ).first()
                
                # If no conversation exists, create a new one
                if not conversation:
                    first_doc = Document.objects.get(id=document_ids[0])
                    conversation = Conversation.objects.create(
                        user=request.user,
                        title=first_doc.title[:50],
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
            
            # Check if streaming is requested
            if stream_mode:
                # Return streaming response
                response = StreamingHttpResponse(
                    self.stream_response(bedrock, message, context, history, conversation, document_ids),
                    content_type='text/event-stream'
                )
                response['Cache-Control'] = 'no-cache'
                # response['X-Accel-Buffering'] = 'no'  # For Nginx
                return response
            else:
                # Generate regular response
                response_text = bedrock.get_response(message, context, history, stream=False)
                
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
                
                # Get all messages
                messages = Message.objects.filter(
                    conversation=conversation
                ).order_by('created_at')
                
                # Create a timeline of events
                timeline = []
                document_added = set()
                
                # Go through messages chronologically
                for msg in messages:
                    # Check if this message references any new documents
                    if msg.role == 'assistant' and msg.references and 'documents' in msg.references:
                        for doc_id in msg.references['documents']:
                            if doc_id not in document_added:
                                # This is the first mention of this document
                                try:
                                    doc = Document.objects.get(id=doc_id)
                                    timeline.append({
                                        'type': 'document_added',
                                        'document_id': doc_id,
                                        'document_title': doc.title,
                                        'created_at': doc.created_at,
                                        'event_time': msg.created_at  # Use message time as event time
                                    })
                                    document_added.add(doc_id)
                                except Document.DoesNotExist:
                                    pass
                    
                    # Add the message to timeline
                    timeline.append({
                        'type': 'message',
                        'id': msg.id,
                        'content': msg.content,
                        'role': msg.role,
                        'created_at': msg.created_at
                    })
                
                # Sort timeline by timestamp
                timeline.sort(key=lambda x: x.get('event_time', x.get('created_at')))
                
                return Response({
                    'conversation': {
                        'id': conversation.id,
                        'title': conversation.title,
                        'created_at': conversation.created_at,
                        'timeline': timeline
                    }
                })
            else:
                # Get all conversations
                conversations = Conversation.objects.filter(
                    user=request.user
                ).order_by('-created_at')
                
                conversation_data = []
                for conv in conversations:
                    # Get document info for this conversation
                    documents = []
                    doc_ids = set()
                    
                    # Find all referenced documents in this conversation
                    for msg in Message.objects.filter(conversation=conv, role='assistant'):
                        if msg.references and 'documents' in msg.references:
                            doc_ids.update(msg.references['documents'])
                    
                    # Get titles for documents
                    for doc_id in doc_ids:
                        try:
                            doc = Document.objects.get(id=doc_id)
                            documents.append({
                                'id': doc_id,
                                'title': doc.title
                            })
                        except Document.DoesNotExist:
                            documents.append({
                                'id': doc_id,
                                'title': "Unknown document"
                            })
                    
                    conversation_data.append({
                        'id': conv.id,
                        'title': conv.title,
                        'created_at': conv.created_at,
                        'message_count': conv.message_set.count(),
                        'documents': documents
                    })
                
                return Response({
                    'conversations': conversation_data
                })
                
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
