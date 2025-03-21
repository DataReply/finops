import os
import json
import boto3  # AWS Textract for document text extraction
import requests  # For interacting with Ollama's API

# AWS Textract client
textract = boto3.client('textract', region_name='eu-central-1')

# Cache file for storing extracted text
data_cache_file = "extracted_text_cache.json"

# Load cached data if available
def load_cached_data():
    if os.path.exists(data_cache_file):
        with open(data_cache_file, "r") as file:
            return json.load(file)
    return {}

# Save extracted text to cache
def save_cached_data(cache):
    with open(data_cache_file, "w") as file:
        json.dump(cache, file, indent=4)

# Function to extract text using AWS Textract
def extract_text_from_pdf_textract(pdf_path):
    with open(pdf_path, 'rb') as document:
        response = textract.analyze_document(
            Document={'Bytes': document.read()},
            FeatureTypes=['TABLES', 'FORMS']  # Extracts structured data if needed
        )
    
    extracted_text = "".join([block['Text'] for block in response['Blocks'] if block['BlockType'] == 'LINE'])
    return extracted_text.strip()

# Function to extract text from PDFs in a directory (including nested folders)
def extract_text_from_pdfs(pdf_directory):
    cached_data = load_cached_data()
    combined_text = ""
    
    for root, _, files in os.walk(pdf_directory):  # Recursively scan all subdirectories
        for filename in files:
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(root, filename)
                
                if filename in cached_data:
#                    print(f"Skipping cached file: {filename}")
                    text = cached_data[filename]
                else:
                    print(f"Processing: {filename}")
                    text = extract_text_from_pdf_textract(pdf_path)
                    cached_data[filename] = text  # Cache the extracted text
                    save_cached_data(cached_data)  # Save cache to file
                
                combined_text += text + "\n\n"  # Add separator between documents
    
    return combined_text

# Function to ask Llama 3 a question using Ollama's API
def ask_ollama(prompt):
    model = "llama3"
#    model = "Mistral"
    url = "http://localhost:11434/api/generate"  # Ollama API endpoint
    payload = {"model": model, "prompt": prompt, "stream": False}
    
    response = requests.post(url, json=payload)
    print('\nModel:', model)
    if response.status_code == 200:
        return response.json().get("response", "No response received")
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

# Main function to process PDFs and answer questions
def process_pdfs_and_answer_questions(pdf_directory, question):
    combined_text = extract_text_from_pdfs(pdf_directory)
    
    prompt = f"Context: {combined_text}\n\nQuestion: {question}\n\nAnswer:"
    answer = ask_ollama(prompt)
    return answer

# Example usage
if __name__ == "__main__":
    pdf_directory = "document-processing/Receipts/"  # Ensure this is a valid path
    question = "Answer only in Yes/No: All invoices are from year 2023 only?"
    
    answer = process_pdfs_and_answer_questions(pdf_directory, question)
    print('\nQuestion:', question)
    print("\nAnswer:", answer)
