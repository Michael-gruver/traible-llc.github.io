from celery import shared_task
from celery.utils.log import get_task_logger
import time

logger = get_task_logger(__name__)

@shared_task(name="test_task")
def test_task():
    """A simple test task to verify Celery is working"""
    logger.info("Test task executed!")
    return "Task completed!"

@shared_task(bind=True, name="process_document_task", 
             time_limit=14400, soft_time_limit=14100,
             autoretry_for=(Exception,),
             retry_kwargs={'max_retries': 3, 'countdown': 60},
             acks_late=True)
def process_document_task(self, document_id):
    """Process a document asynchronously with progress tracking"""
    logger.info(f"Starting to process document {document_id}")
    
    try:
        # Get the document
        from chatbot.models import Document
        document = Document.objects.get(id=document_id)
        
        # Check if this is a resumption
        resuming = False
        start_page = 1
        
        if document.processing_status == "PROCESSING" and document.last_processed_page > 0:
            logger.info(f"Resuming document {document_id} processing from page {document.last_processed_page}")
            resuming = True
            start_page = document.last_processed_page + 1
        else:
            # Update status to processing
            document.processing_status = "PROCESSING"
            document.processing_progress = 0
            document.last_processed_page = 0
            document.save()
        
        logger.info(f"Document {document_id} status updated to PROCESSING")
        
        # Create a BedrockService instance
        from chatbot.services.bedrock_service import BedrockService
        bedrock = BedrockService()
        
        # Process document with progress tracking
        try:
            # If not resuming, extract text from PDF
            if not resuming:
                logger.info(f"Extracting text from document {document_id}")
                document.processing_progress = 5
                document.save()
                
                extracted_text = bedrock.extract_text_from_pdf(document.file.path)
                document.processing_progress = 15
                document.save()
            else:
                # If resuming, load the extracted text from the document
                extracted_text = document.raw_text or ""
                logger.info(f"Using existing extracted text for document {document_id}")
            
            # Get total page count for better progress tracking
            from PyPDF2 import PdfReader
            with open(document.file.path, 'rb') as file:
                pdf_reader = PdfReader(file)
                total_pages = len(pdf_reader.pages)
            
            logger.info(f"Document has {total_pages} pages")
            
            # For memory efficiency, determine chunk size based on document size
            if total_pages > 300:
                chunk_size = 30  # Smaller chunks for very large documents
            elif total_pages > 100:
                chunk_size = 50  # Medium chunks for large documents
            else:
                chunk_size = 100  # Larger chunks for small documents
            
            # Extract rich content page by page with progress updates
            logger.info(f"Extracting rich content from document {document_id}")
            
            # Load existing data if resuming
            if resuming:
                # Load existing data from document
                all_page_data = document.page_data if hasattr(document, 'page_data') and document.page_data else []
                image_data = document.image_data if document.image_data else []
                extracted_tables = document.extracted_tables if document.extracted_tables else []
            else:
                all_page_data = []
                image_data = []
                extracted_tables = []
            
            # Process pages in chunks, starting from the last processed page + 1
            for chunk_start in range(start_page, total_pages + 1, chunk_size):
                chunk_end = min(chunk_start + chunk_size - 1, total_pages)
                logger.info(f"Processing pages {chunk_start} to {chunk_end}")
                
                # Process this chunk of pages
                page_data_chunk = bedrock.extract_rich_content(
                    document.file.path, 
                    page_range=(chunk_start, chunk_end)
                )
                
                # Extract and store only what we need, then clear the chunk to save memory
                for page in page_data_chunk:
                    # Keep track of images and tables
                    if page.get('image_analysis'):
                        image_data.append({
                            'page_number': page['page_number'], 
                            'description': page['image_analysis']
                        })
                    
                    if page.get('tables'):
                        extracted_tables.extend(page['tables'])
                    
                    # Add to full content
                    all_page_data.append({
                        'page_number': page['page_number'],
                        'extracted_text': page.get('extracted_text', ''),
                        'image_analysis': page.get('image_analysis'),
                        'tables': page.get('tables', [])
                    })
                
                # Update progress based on pages processed
                progress = 15 + int(45 * (chunk_end / total_pages))
                document.processing_progress = progress
                document.last_processed_page = chunk_end  # Save the last processed page
                document.save()
                
                # Save intermediate results to avoid losing work if later chunks fail
                document.image_count = len(image_data)
                document.has_images = document.image_count > 0
                document.image_data = image_data
                document.extracted_tables = extracted_tables
                
                # Store page data in a JSON field if available, otherwise in raw_text
                if hasattr(document, 'page_data'):
                    document.page_data = all_page_data
                
                document.save()
                
                # Force garbage collection to free memory
                import gc
                gc.collect()
            
            # Combine text and image descriptions
            logger.info(f"Combining content for document {document_id}")
            full_content = extracted_text + "\n\n"
            for page in all_page_data:
                full_content += f"[PAGE {page['page_number']}]\n"
                full_content += f"Text: {page.get('extracted_text', '')}\n"
                if page.get('image_analysis'):
                    full_content += f"Image Analysis: {page['image_analysis']}\n"
                if page.get('tables'):
                    for table in page['tables']:
                        full_content += "[TABLE]\n" + "\n".join([" | ".join(row) for row in table['rows']]) + "\n\n"
                full_content += "\n"
            
            # Store the processed content
            document.raw_text = full_content
            document.processing_progress = 70
            document.save()
            
            # Clear variables to free memory
            all_page_data = None
            extracted_text = None
            gc.collect()
            
            logger.info(f"Creating embeddings for document {document_id}")
            # Create embeddings and vector store
            texts = bedrock.text_splitter.split_text(full_content)
            
            # Use the method to create or update the vector store
            store_path = bedrock.create_or_update_user_vector_store(
                user_id=document.user.id,
                document_id=document.id,
                texts=texts
            )
            
            document.vector_store_path = store_path
            document.is_processed = True
            document.processing_status = "COMPLETED"
            document.processing_progress = 100
            document.save()
            
            logger.info(f"Document {document_id} processing completed successfully")
            
            success = True
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {str(e)}")
            document.processing_error = str(e)
            document.processing_status = "FAILED"
            document.save()
            success = False
        
        return {
            "status": "success" if success else "failed",
            "document_id": document_id
        }
    except Exception as e:
        logger.error(f"Error in process_document_task for document {document_id}: {str(e)}")
        
        # Update document status if possible
        try:
            from chatbot.models import Document
            document = Document.objects.get(id=document_id)
            document.processing_status = "FAILED"
            document.processing_error = str(e)
            document.save()
        except Exception as inner_e:
            logger.error(f"Error updating document status: {str(inner_e)}")
            
        # Re-raise the exception to mark the task as failed
        raise