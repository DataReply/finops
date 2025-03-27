# Uses python libraries for pdf text extraction
import os
import requests  # For interacting with Ollama's API
import fitz  # PyMuPDF for PDF text extraction
from pdf2image import convert_from_path  # Convert PDFs to images for OCR
import pytesseract  # OCR for text extraction
import re
import nltk
from nltk.corpus import words

# Download English words corpus if not available
nltk.download('words')
english_words = set(words.words())

# Step 1: Function to extract text from a PDF using PyMuPDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as pdf:
            for page in pdf:
                text += page.get_text("text")  # Use "text" mode for better accuracy
    except Exception as e:
        print(f"Error extracting text with PyMuPDF: {e}")
    return text.strip()

# Step 2: OCR-based fallback method (if PyMuPDF gives garbled text)
def extract_text_with_ocr(pdf_path):
    text = ""
    try:
        images = convert_from_path(pdf_path)  # Convert PDF pages to images
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"  # Extract text from image
    except Exception as e:
        print(f"Error extracting text with OCR: {e}")
    return text.strip()

# Step 3: Function to detect encoding issues
def is_garbled_text(text):
    words_in_text = re.findall(r'\b[a-zA-Z]{3,}\b', text)  # Extract words with 3+ letters
    valid_words = [word for word in words_in_text if word.lower() in english_words]
    
    # Calculate percentage of valid English words
    if len(words_in_text) > 0:
        valid_word_ratio = len(valid_words) / len(words_in_text)
    else:
        valid_word_ratio = 0  # No valid words means it's likely garbled
    
    # Check for high special character ratio
    special_chars_ratio = sum(1 for char in text if not char.isalnum() and char not in " \n") / max(len(text), 1)

    # Conditions for garbled text:
    return (
        len(valid_words) < 10 or  # Too few valid words
        valid_word_ratio < 0.2 or  # Less than 20% of words are valid English
        special_chars_ratio > 0.3  # More than 30% of characters are symbols
    )

# Step 4: Function to extract text from all PDFs in a directory
def extract_text_from_pdfs(pdf_directory):
    combined_text = ""
    for filename in os.listdir(pdf_directory):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_directory, filename)
            print(f"Processing: {filename}")

            # Try PyMuPDF first
            text = extract_text_from_pdf(pdf_path)

            # If text appears garbled, fallback to OCR
            if is_garbled_text(text):
                print(f"Text extraction issue detected in {filename}, using OCR...")
                text = extract_text_with_ocr(pdf_path)

            combined_text += text + "\n\n"  # Add separator between documents
    return combined_text

# Step 5: Function to ask Llama 3 a question using Ollama's API
def ask_ollama(prompt, model="llama3"):
    url = "http://localhost:11434/api/generate"  # Ollama API endpoint
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False  # Disable streaming for simplicity
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get("response", "No response received")
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

# Step 6: Main function to process PDFs and answer questions
def process_pdfs_and_answer_questions(pdf_directory, question):
    combined_text = extract_text_from_pdfs(pdf_directory)
    
    prompt = f"Context: {combined_text}\n\nQuestion: {question}\n\nAnswer:"
    answer = ask_ollama(prompt)
    return answer

# Example usage
if __name__ == "__main__":
    pdf_directory = "document-processing/invoice/2024/us/"  # Set your PDF directory path
    question = "Maximum amount paid?"
    
    answer = process_pdfs_and_answer_questions(pdf_directory, question)
    print('\nQuestion:', question)
    print("\nAnswer:", answer)
