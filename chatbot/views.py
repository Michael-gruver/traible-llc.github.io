# chatbot/views.py
from django.http import StreamingHttpResponse, JsonResponse
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
import os
from django.http import FileResponse
from django.db import models

def test_celery(request):
    from .tasks import test_task
    task = test_task.delay()
    return JsonResponse({
        'message': 'Test task queued',
        'task_id': str(task.id)
    })
    
class UserDocumentsListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get all documents for the authenticated user
            documents = Document.objects.filter(user=request.user).order_by('-created_at')
            
            # Prepare the response data
            document_list = []
            for doc in documents:
                document_list.append({
                    'id': doc.id,
                    'title': os.path.basename(doc.file.name),
                    'created_at': doc.created_at,
                    'is_processed': doc.is_processed,
                    'processing_status': getattr(doc, 'processing_status', 'UNKNOWN'),
                    'processing_progress': getattr(doc, 'processing_progress', 0),
                    'page_count': getattr(doc, 'page_count', 0),
                    'has_images': getattr(doc, 'has_images', False),
                    'image_count': getattr(doc, 'image_count', 0),
                    'file_size': doc.file.size if doc.file else 0,
                    'download_url': f"/api/documents/{doc.id}/download/"
                })
            
            return Response({
                'documents': document_list
            })
        
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class DocumentDownloadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, document_id):
        try:
            # Get the document, ensuring it belongs to the authenticated user
            document = Document.objects.get(id=document_id, user=request.user)
            
            # Check if the file exists
            if not document.file or not os.path.exists(document.file.path):
                return Response({
                    'error': 'File not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get the filename
            filename = os.path.basename(document.file.name)
            
            # Return the file as a response
            response = FileResponse(
                open(document.file.path, 'rb'),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
        
        except Document.DoesNotExist:
            return Response({
                'error': 'Document not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            # Calculate file hash
            bedrock = BedrockService()
            file_hash = bedrock.calculate_file_hash(file)
            
            # Check for existing document
            existing_document = Document.objects.filter(
                user=request.user,
                file_hash=file_hash
            ).first()
            
            if existing_document:
                return Response({
                    'message': 'Document with this name already exists',
                    'document_id': existing_document.id,
                    'is_processed': existing_document.is_processed,
                    'processing_status': existing_document.processing_status
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Save new document
            document = Document.objects.create(
                user=request.user,
                title=file.name,
                file=file,
                content_type=content_type,
                file_hash=file_hash,
                is_processed=False,
                processing_status='PENDING',
                processing_progress=0
            )
            
            print(f"Document created with ID: {document.id}, now queueing task")
            
            # Queue the document for processing
            from chatbot.tasks import process_document_task
            task = process_document_task.delay(document.id)
            
            print(f"Task queued with ID: {task.id}")
            
            # Store the task ID for future reference
            document.task_id = task.id
            document.save()
            
            return Response({
                'message': 'Document uploaded and queued for processing',
                'document_id': document.id,
                'processing_status': 'PENDING',
                'title':file.name
            })
            
        except Exception as e:
            print(f"Error in document upload: {str(e)}")
            return Response({
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DocumentStatusView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, document_id=None):
        try:
            if document_id:
                # Get specific document status
                document = get_object_or_404(Document, id=document_id, user=request.user)
                
                return Response({
                    'document_id': document.id,
                    'title': document.title,
                    'is_processed': document.is_processed,
                    'processing_status': document.processing_status,
                    'processing_progress': document.processing_progress,
                    'processing_error': document.processing_error,
                    'has_images': document.has_images,
                    'image_count': document.image_count,
                    'created_at': document.created_at
                })
            else:
                # Get all documents for the user
                documents = Document.objects.filter(user=request.user).order_by('-created_at')
                
                return Response({
                    'documents': [{
                        'document_id': doc.id,
                        'title': doc.title,
                        'is_processed': doc.is_processed,
                        'processing_status': doc.processing_status,
                        'processing_progress': doc.processing_progress,
                        'created_at': doc.created_at
                    } for doc in documents]
                })
                
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class DocumentUploadView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def post(self, request):
#         if 'file' not in request.FILES:
#             return Response({
#                 'message': 'No file provided'
#             }, status=status.HTTP_400_BAD_REQUEST)
            
#         file = request.FILES['file']
#         content_type = mimetypes.guess_type(file.name)[0]
        
#         if content_type != 'application/pdf':
#             return Response({
#                 'message': 'Only PDF files are supported'
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             # Calculate file hash
#             bedrock = BedrockService()
#             file_hash = bedrock.calculate_file_hash(file)
            
#             # Check for existing document
#             existing_document = Document.objects.filter(
#                 user=request.user,
#                 file_hash=file_hash
#             ).first()
            
#             if existing_document:
#                 return Response({
#                     'message': 'Document with this name already exists',
#                     'document_id': existing_document.id,
#                     'is_processed': existing_document.is_processed,
#                     'processing_status': existing_document.processing_status
#                 }, status=status.HTTP_400_BAD_REQUEST)
            
#             # Save new document
#             document = Document.objects.create(
#                 user=request.user,
#                 title=file.name,
#                 file=file,
#                 content_type=content_type,
#                 file_hash=file_hash,
#                 is_processed=False,
#                 processing_status='PENDING',
#                 processing_progress=0
#             )
            
#             # Queue the document for processing
#             from .tasks import process_document_task
#             task = process_document_task.delay(document.id)
            
#             # Store the task ID for future reference
#             document.task_id = task.id
#             document.save()
            
#             return Response({
#                 'message': 'Document uploaded and queued for processing',
#                 'document_id': document.id,
#                 'processing_status': 'PENDING'
#             })
            
#         except Exception as e:
#             return Response({
#                 'message': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
# class DocumentStatusView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request, document_id):
#         try:
#             document = get_object_or_404(Document, id=document_id, user=request.user)
            
#             return Response({
#                 'document_id': document.id,
#                 'title': document.title,
#                 'is_processed': document.is_processed,
#                 'processing_status': document.processing_status,
#                 'processing_progress': document.processing_progress,
#                 'processing_error': document.processing_error,
#                 'has_images': document.has_images,
#                 'image_count': document.image_count,
#                 'created_at': document.created_at
#             })
#         except Exception as e:
#             return Response({
#                 'message': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        stream_mode = request.data.get('stream', False)
        stream_mode = request.data.get('stream', False)
        
        if not message:
            return Response({
                'message': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if not document_ids:
            return Response({
                'message': 'At least one document is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Verify all documents exist and are processed
            accessible_docs = Document.objects.filter(
                models.Q(user=request.user)
            ).distinct()
            
            
            for doc_id in document_ids:
                doc = accessible_docs.filter(id=doc_id).first()
                
                if not doc:
                    return Response({
                        'message': f'Document {doc_id} not found or you do not have access to it'
                    }, status=status.HTTP_404_NOT_FOUND)
                    
                if not doc.is_processed:
                    return Response({
                        'message': f'Document {doc_id} is not processed yet. Please wait and try again.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                doc = accessible_docs.filter(id=doc_id).first()
                
                if not doc:
                    return Response({
                        'message': f'Document {doc_id} not found or you do not have access to it'
                    }, status=status.HTTP_404_NOT_FOUND)
                    
                if not doc.is_processed:
                    return Response({
                        'message': f'Document {doc_id} is not processed yet. Please wait and try again.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create conversation
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(
                        id=conversation_id,
                        user=request.user
                    )
                    
                    # Update conversation title with first message if it's still the generic title
                    if conversation.title == 'Untitled Conversation':
                        conversation.title = message[:50]
                        conversation.save()
                
                    
                    # Update conversation title with first message if it's still the generic title
                    if conversation.title == 'Untitled Conversation':
                        conversation.title = message[:50]
                        conversation.save()
                
                except Conversation.DoesNotExist:
                    return Response({
                        'message': 'Conversation not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:

                # Create a new conversation
                conversation = Conversation.objects.create(
                    user=request.user,
                    title=message[:50],  # Set title as first message
                    document_key='-'.join(sorted(document_ids))
                )
            
            # Save user message
            Message.objects.create(
                conversation=conversation,
                content=message,
                role='user'
            )
            # print(f"Message: {message}")
            # print(f"Document IDs: {document_ids}")
            # Get document context
            bedrock = BedrockService()
            serach_results, errors = bedrock.search_documents(
                # request.user, 
                message, 
                # top_k=5
                document_ids,
                request.user.id
            )
            if errors:
                print(f"errors during document search: {errors}")
                
            relevant_docs = []
            for doc in serach_results:
                #check if this is a document object with
                if hasattr(doc, 'page_content'):
                    relevant_docs.append(doc)
                elif isinstance(doc, dict) and 'page_content' in doc:
                    relevant_docs.append(doc)
                elif isinstance(doc, list):
                    if not doc:
                        continue
                    if hasattr(doc[0], 'page_content'):
                        relevant_docs.extend(doc)
                    else:
                        print(f"Unexpected document format: {type(doc[0])}")
                        
            print(f"Found {len(relevant_docs)} relevant documents after processing")
            if len(relevant_docs) > 0:
                print(f"First document: {relevant_docs[0].page_content[:100]}")
                        
            # context = "\n\n".join([doc[0].page_content for doc in relevant_docs])
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
                        'contexts': [doc.page_content for doc in relevant_docs if hasattr(doc, 'page_content')]
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
            if not conversation_id:
                # Get all conversations
                conversations = Conversation.objects.filter(
                    user=request.user
                ).order_by('-created_at')
                
                conversation_data = []
                for conv in conversations:
                    # Get first user message as title
                    first_message = Message.objects.filter(
                        conversation=conv, 
                        role='user'
                    ).order_by('created_at').first()
                    
                    # Find all referenced documents in this conversation
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
                        'title': first_message.content[:50] if first_message else conv.title,
                        'created_at': conv.created_at,
                        'message_count': conv.message_set.count(),
                        'documents': documents
                    })
                
                return Response({
                    'conversations': conversation_data
                })
            
            if not conversation_id:
                # Get all conversations
                conversations = Conversation.objects.filter(
                    user=request.user
                ).order_by('-created_at')
                
                conversation_data = []
                for conv in conversations:
                    # Get first user message as title
                    first_message = Message.objects.filter(
                        conversation=conv, 
                        role='user'
                    ).order_by('created_at').first()
                    
                    # Find all referenced documents in this conversation
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
                        'title': first_message.content[:50] if first_message else conv.title,
                        'created_at': conv.created_at,
                        'message_count': conv.message_set.count(),
                        'documents': documents
                    })
                
                return Response({
                    'conversations': conversation_data
                })
            
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
                        'title': messages.filter(role='user').first().content[:50] if messages.filter(role='user').exists() else conversation.title,
                        'title': messages.filter(role='user').first().content[:50] if messages.filter(role='user').exists() else conversation.title,
                        'created_at': conversation.created_at,
                        'timeline': timeline
                    }
                })
            
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
# In chatbot/views.py
class ConversationDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, conversation_id):
        try:
            # Find the conversation for the current authenticated user
            conversation = get_object_or_404(
                Conversation, 
                id=conversation_id, 
                user=request.user
            )
            
            # Delete all associated messages
            Message.objects.filter(conversation=conversation).delete()
            
            # Delete the conversation
            conversation.delete()
            
            return Response({
                'message': 'Conversation deleted successfully'
            }, status=status.HTTP_200_OK)
        
        except Conversation.DoesNotExist:
            return Response({
                'message': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'message': 'Error deleting conversation',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
# In chatbot/views.py
class UserDocumentsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Retrieve all documents uploaded by the user
            documents = Document.objects.filter(
                user=request.user
            ).order_by('-created_at')
            
            # Serialize document information
            document_data = [{
                'id': doc.id,
                'title': doc.title,
                'is_processed': doc.is_processed,
                'created_at': doc.created_at,
                'content_type': doc.content_type
            } for doc in documents]
            
            return Response({
                'documents': document_data
            })
        
            
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
# In chatbot/views.py
class ConversationDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, conversation_id):
        try:
            # Find the conversation for the current authenticated user
            conversation = get_object_or_404(
                Conversation, 
                id=conversation_id, 
                user=request.user
            )
            
            # Delete all associated messages
            Message.objects.filter(conversation=conversation).delete()
            
            # Delete the conversation
            conversation.delete()
            
            return Response({
                'message': 'Conversation deleted successfully'
            }, status=status.HTTP_200_OK)
        
        except Conversation.DoesNotExist:
            return Response({
                'message': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'message': 'Error deleting conversation',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
# In chatbot/views.py
class UserDocumentsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Add a query parameter option to filter by processing status
            show_all = request.query_params.get('show_all', 'false').lower() == 'true'
            
            # Retrieve all documents uploaded by the user
            query = Document.objects.filter(
                user=request.user
            )
            
            # Apply processing filter unless show_all is true
            if not show_all:
                query = query.filter(is_processed=True)
            
            # Get the documents ordered by creation date
            documents = query.order_by('-created_at')
            
            # Serialize document information
            document_data = [{
                'id': doc.id,
                'title': doc.title,
                'is_processed': doc.is_processed,
                'created_at': doc.created_at,
                'content_type': doc.content_type
            } for doc in documents]
            
            return Response({
                'documents': document_data
            })
        
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    # In chatbot/views.py
class ConversationInitializeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Get optional document IDs from request
        document_ids = request.data.get('document_ids', [])
        
        try:
            # Validate documents
            if document_ids:
                # Ensure user has access to these documents
                documents = Document.objects.filter(
                    user=request.user, 
                    id__in=document_ids, 
                    is_processed=True
                )
                
                if len(documents) != len(document_ids):
                    return Response({
                        'message': 'One or more documents not found or not processed'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create a new conversation with a generic initial title
            conversation = Conversation.objects.create(
                user=request.user,
                title='Untitled Conversation',  # Generic initial title
                document_key='-'.join(sorted(map(str, document_ids))) if document_ids else None
            )
            
            return Response({
                'conversation_id': str(conversation.id),
                'documents': [
                    {
                        'id': doc.id, 
                        'title': doc.title
                    } for doc in documents
                ] if document_ids else []
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # In chatbot/views.py
class ConversationInitializeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Get optional document IDs from request
        document_ids = request.data.get('document_ids', [])
        
        try:
            # Validate documents
            if document_ids:
                # Ensure user has access to these documents
                documents = Document.objects.filter(
                    user=request.user, 
                    id__in=document_ids, 
                    is_processed=True
                )
                
                if len(documents) != len(document_ids):
                    return Response({
                        'message': 'One or more documents not found or not processed'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create a new conversation with a generic initial title
            conversation = Conversation.objects.create(
                user=request.user,
                title='Untitled Conversation',  # Generic initial title
                document_key='-'.join(sorted(map(str, document_ids))) if document_ids else None
            )
            
            return Response({
                'conversation_id': str(conversation.id),
                'documents': [
                    {
                        'id': doc.id, 
                        'title': doc.title
                    } for doc in documents
                ] if document_ids else []
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
# In views.py
class DocumentDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, document_id):
        try:
            # Find the document for the current authenticated user
            document = get_object_or_404(
                Document, 
                id=document_id, 
                user=request.user
            )
            
            # Check if the document is still being processed
            if not document.is_processed:
                return Response({
                    'message': 'Cannot delete document that is still being processed. Please wait until processing is complete or upload a new document.',
                    'document_id': document_id,
                    'processing_status': document.processing_status if hasattr(document, 'processing_status') else 'UNKNOWN',
                    'processing_progress': document.processing_progress if hasattr(document, 'processing_progress') else 0
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the file path and vector store path before deleting the document
            file_path = document.file.path if document.file else None
            vector_store_path = document.vector_store_path if hasattr(document, 'vector_store_path') and document.vector_store_path else None
            
            # Delete the document from the database
            document.delete()
            
            # Remove the physical file if it exists
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Removed file {file_path}")
                    
                    # Also remove the directory if it's empty
                    directory = os.path.dirname(file_path)
                    if os.path.exists(directory) and not os.listdir(directory):
                        os.rmdir(directory)
                        print(f"Removed empty directory {directory}")
                except Exception as e:
                    print(f"Error removing file: {str(e)}")
            
            # Clean up vector store if it exists
            if vector_store_path and os.path.exists(vector_store_path):
                try:
                    import shutil
                    shutil.rmtree(vector_store_path)
                    print(f"Removed vector store directory {vector_store_path}")
                except Exception as e:
                    print(f"Error removing vector store: {str(e)}")
            
            return Response({
                'message': 'Document deleted successfully'
            }, status=status.HTTP_200_OK)
        
        except Document.DoesNotExist:
            return Response({
                'message': 'Document not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error in document delete: {str(e)}")
            return Response({
                'message': 'Error deleting document',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)