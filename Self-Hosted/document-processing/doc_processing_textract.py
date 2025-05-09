# Uses AWS textract for text extraction
# Simple Yes/No questions related to receipt text are asked
import os
import json
import boto3  # AWS Textract for document text extraction
import requests  # For interacting with Ollama's API
import time

# AWS Textract client
textract = boto3.client('textract', region_name='eu-central-1')

# Cache file for storing extracted text
data_cache_file = "Self-Hosted/document-processing/extracted_text_cache.json"

questions = [
        "Answer just in Yes or No: All invoices belong to year 2023 only?",
        "Answer just in Yes or No: Any receipt for Cheese Cake Factory?",
        "Answer just in Yes or No: Any invoice of Starbucks?",
        "Answer just in Yes or No: All receipts belong to year 2023 or 2024 only?",
        "Answer just in Yes or No: Total amount paid at Cafe Gelato was 31.28 dollars?",
        "Answer just in Yes or No: Total amount paid at McDonald's was 12.90 euros?",
        "Answer just in Yes or No: Maximum total amount was paid at Jimmy's?",
        "Answer just in Yes or No: Maximum tax was paid at Jimmy's?",
        "Answer just in Yes or No: Any receipt from year 2022?",
        "Answer just in Yes or No: Maximum discount was given at Old Navy?"
    ]

ground_truths = ["No", "Yes", "No", "Yes", "Yes", "No", "Yes", "No", "No", "Yes"]

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
            FeatureTypes=['TABLES', 'FORMS']
        )
    extracted_text = "".join([block['Text'] for block in response['Blocks'] if block['BlockType'] == 'LINE'])
    return extracted_text.strip()

# Function to extract text from PDFs in a directory
def extract_text_from_pdfs(pdf_directory):
    cached_data = load_cached_data()
    combined_text = ""
    
    for root, _, files in os.walk(pdf_directory):
        for filename in files:
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(root, filename)
                
                if filename in cached_data:
                    print(f"Skipping cached file: {filename}")
                    text = cached_data[filename]
                else:
                    print(f"Processing: {filename}")
                    text = extract_text_from_pdf_textract(pdf_path)
                    cached_data[filename] = text
                    save_cached_data(cached_data)             
                combined_text += text + "\n\n"
    
    return combined_text

# Function to query a model via Ollama API
def ask_ollama(model, prompt):
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, "prompt": prompt, "temperature": 0.2, "stream": False}
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get("response", "No response received")[:4]
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

# Main function to process PDFs and answer questions
def process_pdfs_and_answer_questions(pdf_directory, questions, iterations):
    combined_text = extract_text_from_pdfs(pdf_directory)
    
    for i in range(iterations):
        print(f"\nIteration {i+1}:")
        for idx, question in enumerate(questions):
            prompt = f"Context: {combined_text}\n\nQuestion: {question}\n\nAnswer:"
            llama_answer = ask_ollama("llama3", prompt)
            ground_truth = ground_truths[idx]
            
            print(f"\nQuestion: {question}")
            print(f"Llama3 Answer: {llama_answer}")
            print(f"Ground Truth: {ground_truth}")

    for i in range(iterations):
        print(f"\nIteration {i+1}:")
        for idx, question in enumerate(questions):
            prompt = f"Context: {combined_text}\n\nQuestion: {question}\n\nAnswer:"
            mistral_answer = ask_ollama("mistral", prompt)
            ground_truth = ground_truths[idx]
            
            print(f"\nQuestion: {question}")
            print(f"Mistral Answer: {mistral_answer}")
            print(f"Ground Truth: {ground_truth}")

# Example usage
if __name__ == "__main__":
    start = time.time()
    pdf_directory = "Self-Hosted/document-processing/Receipts"
    process_pdfs_and_answer_questions(pdf_directory, questions, iterations=10)
    end = time.time()
    total_time = end - start
    print("\nTotal Execution time:"+ str(total_time))