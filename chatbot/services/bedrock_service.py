# chatbot/services/bedrock_service.py

import boto3
from langchain_aws import BedrockEmbeddings  # Updated import
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader  # Updated import
import json
import os

class BedrockService:
    def __init__(self):
        # Initialize Bedrock client
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1',
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

    def process_document(self, document):
        """Process document and create embeddings"""
        try:
            # Load document
            if document.content_type == 'application/pdf':
                loader = PyPDFLoader(document.file.path)
                pages = loader.load()
                
                # Split into chunks
                texts = self.text_splitter.split_documents(pages)
                
                # Create vector store
                vector_store = FAISS.from_documents(texts, self.embeddings)
                
                # Save vector store
                store_path = f'vector_stores/{document.id}'
                os.makedirs(store_path, exist_ok=True)
                vector_store.save_local(store_path)
                
                document.vector_store_path = store_path
                document.is_processed = True
                document.save()
                
                return True
            else:
                raise ValueError(f"Unsupported file type: {document.content_type}")
                
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            return False

    def get_response(self, question, context, conversation_history=None):
        """Generate response using Claude with guardrails"""
        try:
            if not context.strip():
                return "No relevant context found in the documents. Please check if the document was processed correctly."
            
            # Create messages array
            messages = []
            
            # Add the initial user message with context
            messages.append({
                "role": "user",
                "content": f"Here is the context from the documents:\n\n{context}\n\nQuestion: {question}"
            })

            # Add conversation history while ensuring alternating roles
            if conversation_history:
                current_role = "assistant"  # Start with assistant since last message was user
                for msg in conversation_history:
                    if msg.role == current_role:
                        messages.append({
                            "role": msg.role,
                            "content": msg.content
                        })
                        # Switch role for next message
                        current_role = "user" if current_role == "assistant" else "assistant"

            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": messages,
                "temperature": 0.7
            })
            
            response = self.bedrock_runtime.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                body=body
            )
        
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            print(f"Error in get_response: {str(e)}")
            raise

    def search_documents(self, query, document_ids):
        """Search across multiple documents"""
        results = []
        
        for doc_id in document_ids:
            vector_store = FAISS.load_local(
                f'vector_stores/{doc_id}',
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            docs = vector_store.similarity_search(query, k=2)
            results.extend(docs)
        
        return results