import boto3
from botocore.config import Config
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import json
import os
from pdf2image import convert_from_path
import pytesseract
from PyPDF2 import PdfReader
from PIL import Image
import tempfile
import hashlib
import numpy as np
import cv2
import base64
from io import BytesIO
from django.conf import settings

class BedrockService:
    def __init__(self):
        # Initialize Bedrock client
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1',
            aws_access_key_id='AKIAXTORPSTXNZXE2AWM',
            aws_secret_access_key='***REMOVED***',
            config=Config(
                retries={'max_attempts': 3, 'mode': 'standard'},
                connect_timeout=5,
                read_timeout=60
            )
        )
        
        self.textract_client = boto3.client(
            service_name='textract',
            region_name= 'us-east-1',
            aws_access_key_id='AKIAXTORPSTXNZXE2AWM',
            aws_secret_access_key='***REMOVED***'
        )
        
        # Initialize embeddings
        self.embeddings = BedrockEmbeddings(
            client=self.bedrock_runtime,
            model_id="amazon.titan-embed-text-v1"
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def calculate_file_hash(self, file):
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        for chunk in file.chunks():
            hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def create_or_update_user_vector_store(self, user_id, document_id, texts):
        """Create or update a vector store for a specific user's document"""
        try:
            # Create a unique path for the user's vector store
            store_path = f'vector_stores/user_{user_id}/document_{document_id}'
            os.makedirs(store_path, exist_ok=True)

            # Check if a vector store already exists
            if os.path.exists(os.path.join(store_path, 'index.faiss')):
                # Load existing vector store
                vector_store = FAISS.load_local(store_path, self.embeddings)
                # Add new texts to the existing vector store
                vector_store.add_texts(texts)
            else:
                # Create a new vector store
                vector_store = FAISS.from_texts(texts, self.embeddings)

            # Save the vector store
            vector_store.save_local(store_path)

            return store_path
        except Exception as e:
            print(f"Error creating/updating vector store: {str(e)}")
            raise

    def process_document(self, document):
        """Process document and create embeddings"""
        try:
            # Extract text and rich content from PDF
            extracted_text = self.extract_text_from_pdf(document.file.path)
            page_data = self.extract_rich_content(document.file.path)
            
            # Combine text and image descriptions
            full_content = extracted_text + "\n\n"
            for page in page_data:
                full_content += f"[PAGE {page['page_number']}]\n"
                full_content += f"Text: {page['extracted_text']}\n"
                if page['image_analysis']:
                    full_content += f"Image Analysis: {page['image_analysis']}\n"
                if page['tables']:
                    for table in page['tables']:
                        full_content += "[TABLE]\n" + "\n".join([" | ".join(row) for row in table['rows']]) + "\n\n"
                full_content += "\n"
            
            # Store the processed content
            document.raw_text = full_content
            document.has_images = any(page['image_analysis'] is not None for page in page_data)
            document.image_count = sum(1 for page in page_data if page['image_analysis'] is not None)
            document.image_data = [{'page_number': page['page_number'], 'description': page['image_analysis']} for page in page_data if page['image_analysis'] is not None]
            document.extracted_tables = [table for page in page_data for table in page['tables']]
            
            # Create embeddings and vector store
            texts = self.text_splitter.split_text(full_content)
            
            print(f"Texts: {texts}")
            # Use the new method to create or update the vector store
            store_path = self.create_or_update_user_vector_store(
                user_id=document.user.id,
                document_id=document.id,
                texts=texts
            )
            
            document.vector_store_path = store_path
            document.is_processed = True
            document.save()
            
            return True
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            document.processing_error = str(e)
            document.save()
            return False

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF using PyPDF2"""
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text

    def extract_rich_content(self, pdf_path):
        """Extract text, images, diagrams, and tables from PDF"""
        page_data = []

        try:
            # Convert PDF pages to images
            images = convert_from_path(pdf_path)

            for page_num, image in enumerate(images, start=1):
                # Save image to temp file
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                    image.save(temp_file, format="PNG")
                    temp_image_path = temp_file.name

                # Process the image
                img_cv = cv2.imread(temp_image_path)
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
                # Check if page is mostly blank
                if np.mean(gray) > 250:
                    print(f"🚫 Skipping blank page {page_num}")
                    os.unlink(temp_image_path)
                    continue

                # Extract text using OCR
                extracted_text = pytesseract.image_to_string(gray)

                # Detect if page contains significant non-text elements
                edges = cv2.Canny(gray, 100, 200)
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                significant_contours = [c for c in contours if cv2.contourArea(c) > 1000]

                image_analysis = None
                tables = []

                if len(significant_contours) > 0:
                    # Use Textract for comprehensive analysis
                    with open(temp_image_path, "rb") as img_file:
                        img_bytes = img_file.read()
                
                    response = self.textract_client.analyze_document(
                        Document={'Bytes': img_bytes},
                        FeatureTypes=['TABLES', 'FORMS']
                    )
                
                    # Extract tables
                    table_blocks = [b for b in response.get('Blocks', []) if b.get('BlockType') == 'TABLE']
                    for table_block in table_blocks:
                        table_data = self._process_table(table_block, response.get('Blocks', []))
                        tables.append(table_data)
                
                    # Analyze image with Claude Vision
                    image_analysis = self.analyze_technical_image(temp_image_path, page_num)

                # Store page information
                page_info = {
                    'page_number': page_num,
                    'extracted_text': extracted_text,
                    'image_path': temp_image_path,
                    'image_analysis': image_analysis,
                    'tables': tables
                }
                page_data.append(page_info)
                print(f"✅ Processed page {page_num}: text and {'image' if image_analysis else 'no image'} content")

            # Clean up temporary files
            for page in page_data:
                if os.path.exists(page['image_path']):
                    os.unlink(page['image_path'])

        except Exception as e:
            print(f"Error extracting rich content: {e}")

        return page_data

    def _process_table(self, table_block, all_blocks):
        """Process a table block from Textract response"""
        table_id = table_block['Id']
        table_cells = [b for b in all_blocks if b['BlockType'] == 'CELL' and any(rel['Ids'][0] == table_id for rel in b.get('Relationships', []) if rel['Type'] == 'CHILD')]
        
        rows = {}
        for cell in table_cells:
            row_index = cell['RowIndex']
            col_index = cell['ColumnIndex']
            if row_index not in rows:
                rows[row_index] = {}
            
            cell_content = cell.get('Text', '')
            rows[row_index][col_index] = cell_content

        table_data = []
        for row_idx in sorted(rows.keys()):
            row = [rows[row_idx].get(col_idx, '') for col_idx in sorted(rows[row_idx].keys())]
            table_data.append(row)

        return {'rows': table_data}

    def analyze_technical_image(self, image_path, page_num):
        """Use Claude 3 Vision to analyze technical diagrams"""
        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()

            base64_image = base64.b64encode(image_bytes).decode("utf-8")

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this image in detail. If it contains machinery or technical diagrams, please provide:
1. The type and purpose of the equipment or diagram
2. Main components visible in the image
3. Key features or mechanisms shown
4. Any visible safety features
5. The general operating principle or purpose of what's shown

If the image contains other content, please describe it accurately and concisely."""
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": base64_image
                            }
                        }
                    ]
                }
            ]

            model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1500,
                    "messages": messages,
                    "temperature": 0.2
                })
            )

            response_body = json.loads(response['body'].read())
            print(f"✅ Image analyzed on page {page_num}")

            if 'content' in response_body and response_body['content']:
                return response_body['content'][0]['text']

            return "No relevant information extracted from the image."

        except Exception as e:
            print(f"Error analyzing image: {e}")
            return f"Error analyzing image: {str(e)}"

    def get_relevant_context(self, question, document_id):
        """Retrieve relevant context for a given question from a specific document"""
        try:
            vector_store = FAISS.load_local(
                f'vector_stores/{document_id}',
                self.embeddings
            )
            relevant_docs = vector_store.similarity_search(question, k=3)
            
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            # If the question seems to be about machinery or images, include full image analyses
            if any(keyword in question.lower() for keyword in ["machine", "equipment", "diagram", "image", "picture", "how does it work", "machinery"]):
                from chatbot.models import Document  # Import here to avoid circular import
                document = Document.objects.get(id=document_id)
                for image_data in document.image_data:
                    context += f"\n\nImage Analysis (Page {image_data['page_number']}):\n{image_data['description']}"
            
            print(f"Context in get relevant function: {context}")
            return context
        except Exception as e:
            print(f"Error getting relevant context: {str(e)}")
            return ""

    def get_response(self, question, context, conversation_history=None, stream=False):
        try:
            # Check if the question is about diagrams or images
            is_image_question = any(keyword in question.lower() for keyword in 
                                ["diagram", "image", "picture", "illustration", "figure", "schematic", "cover", "page 1"])
            
            # Enhance the prompt for image questions
            if is_image_question:
                image_prompt = """
                IMPORTANT: The context contains descriptions of images and diagrams from the document. 
                When answering, focus on the image descriptions, especially those from the page mentioned in the question.
                """
                print(f"Image-related question detected. Adding special prompt.")
            else:
                image_prompt = ""
                
            if not context.strip():
                print("Warning: Empty context provided")
                return "No relevant context found in the documents. Please check if the document was processed correctly."
        
            

            # Prepare the messages
            messages = [
                {
                    "role": "user",
                    "content": f"""Context: {context}
                    
                {image_prompt}
                Question: {question}

                Please provide a detailed answer based on the context. If the question is about machinery or diagrams, include relevant technical details from the image analysis and textual descriptions."""
                                }
                            ]

            if conversation_history:
                last_role = "user"
                for msg in conversation_history:
                    if msg.role != last_role:
                        messages.append({
                            "role": "user" if msg.role == "user" else "assistant",
                            "content": msg.content
                        })
                        last_role = msg.role
            

            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": messages,
                "temperature": 0.2  # Lowered temperature for more focused responses
            })
        
            model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        
            if stream:
                response_stream = self.bedrock_runtime.invoke_model_with_response_stream(
                    modelId=model_id,
                    body=body
                )
                
                full_response = ""
            
                for event in response_stream["body"]:
                    if "chunk" in event:
                        chunk_data = json.loads(event["chunk"]["bytes"].decode())
                        if "delta" in chunk_data and "text" in chunk_data["delta"]:
                            full_response += chunk_data["delta"]["text"]
                            yield chunk_data["delta"]["text"]
                print(f'response from the bedrock: {full_response}')
                return 
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=body
            )
        
            response_body = json.loads(response['body'].read())
            if 'content' in response_body and response_body['content']:
                return response_body['content'][0]['text']
            else:
                return "I couldn't find relevant information to answer the question based on the provided context. Could you please rephrase or ask about a different aspect of the document?"
            
        except Exception as e:
            error_message = f"Error in get_response: {str(e)}"
            print(error_message)
            return error_message

    # def search_documents(self, query, document_ids, user_id):
    #     """Search across multiple documents"""
    #     results = []
    #     errors = []
        
    #     for doc_id in document_ids:
    #         try:
    #             vector_store_path = f'vector_stores/user_{user_id}/document_{doc_id}'
    #             print(f"Attempting to load vector store from: {vector_store_path}")
    #             if not os.path.exists(vector_store_path):
    #                 print(f"Vector store path does not exist: {vector_store_path}")  # Add this line for debugging
    #                 continue  # Skip to the next document if the path doesn't exist
                
    #             if not os.path.exists(os.path.join(vector_store_path, 'index.faiss')):
    #                 print(f"FAISS index not found in: {vector_store_path}")
    #                 errors.append(f"FAISS index not found for document {doc_id}")
    #                 continue
                
    #             vector_store = FAISS.load_local(
    #                 vector_store_path,
    #                 self.embeddings,
    #                 allow_dangerous_deserialization=True
    #             )
    #             docs = vector_store.similarity_search(query, k=2)
    #             results.extend(docs)
    #             print(f"Successfully searched document {doc_id}")
    #         except Exception as e:
    #             print(f"Error searching document {doc_id}: {e}")
                
    #     return results

    def search_documents(self, query, document_ids, user_id):
        # print(document_ids)
        """Search across multiple documents with enhanced diagram retrieval"""
        results = []
        errors = []
        is_diagram_query = any(keyword in query.lower() for keyword in ["diagram", "image", "picture", "illustration", "figure", "schematic", "machinery", "machine"])
        
        for doc_id in document_ids:
            try:
                vector_store_path = f'vector_stores/user_{user_id}/document_{doc_id}'
                print(f"Attempting to load vector store from: {vector_store_path}")
                
                if not os.path.exists(vector_store_path):
                    print(f"Vector store path does not exist: {vector_store_path}")
                    errors.append(f"Vector store not found for document {doc_id}")
                    continue
                
                if not os.path.exists(os.path.join(vector_store_path, 'index.faiss')):
                    print(f"FAISS index not found in: {vector_store_path}")
                    errors.append(f"FAISS index not found for document {doc_id}")
                    continue
                
                # Load the vector store
                vector_store = FAISS.load_local(
                    vector_store_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                
                # For diagram queries, use more results and different search parameters
                if is_diagram_query:
                    # print("hereeeeeeeeeeeeeeeee")
                    # Use more results for diagram queries to increase chances of finding relevant content
                    docs = vector_store.similarity_search(query, k=4)
                    
                    # Also explicitly search for diagram-related content
                    diagram_docs = vector_store.similarity_search("diagram image illustration figure machinery machine", k=2)
                    
                    # Combine results, removing duplicates - FIXED THIS PART
                    all_docs = []
                    all_docs.extend(docs)
                    for doc in diagram_docs:
                        if not any(doc.page_content == d.page_content for d in docs):
                            all_docs.append(doc)
                    
                    results.extend(all_docs)
                    
                    # If this is a diagram query, also fetch image data directly from the database
                    try:
                        from chatbot.models import Document  # Import here to avoid circular import
                        document = Document.objects.get(id=doc_id)
                        
                        if document.has_images and document.image_data:
                            print(f"Found {len(document.image_data)} images in document {doc_id}")
                            
                            # Create synthetic documents from image data to include in results
                            for img_data in document.image_data:
                                # Create a document-like object with the image description
                                from langchain.schema import Document as LangchainDocument
                                img_doc = LangchainDocument(
                                    page_content=f"Image on page {img_data['page_number']}: {img_data['description']}",
                                    metadata={"source": f"document_{doc_id}_image_{img_data['page_number']}"}
                                )
                                results.append(img_doc)
                    except Exception as img_error:
                        print(f"Error retrieving image data from database: {str(img_error)}")
                else:
                    # Standard search for non-diagram queries
                    docs = vector_store.similarity_search(query, k=2)
                    results.extend(docs)
                    
                print(f"Successfully searched document {doc_id}")
            except Exception as e:
                error_msg = f"Error searching document {doc_id}: {str(e)}"
                print(error_msg)
                errors.append(error_msg)
        
        # If this is a diagram query but no results were found, add a note about it
        if is_diagram_query and not results:
            from langchain.schema import Document as LangchainDocument
            no_diagrams_doc = LangchainDocument(
                page_content="Note: Your query appears to be about diagrams or images, but no specific diagram information was found in the search results.",
                metadata={"source": "system_message"}
            )
            results.append(no_diagrams_doc)
        
        return results, errors