import os
import json
import boto3  # AWS SDK for Textract and Bedrock

# AWS Clients
textract = boto3.client('textract', region_name='eu-central-1')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='eu-west-2')  # Bedrock requires specific regions

data_cache_file = "extracted_text_cache.json"

def load_cached_data():
    if os.path.exists(data_cache_file):
        with open(data_cache_file, "r") as file:
            return json.load(file)
    return {}

def save_cached_data(cache):
    with open(data_cache_file, "w") as file:
        json.dump(cache, file, indent=4)

def extract_text_from_pdf_textract(pdf_path):
    with open(pdf_path, 'rb') as document:
        response = textract.analyze_document(
            Document={'Bytes': document.read()},
            FeatureTypes=['TABLES', 'FORMS']
        )
    extracted_text = "".join([block['Text'] for block in response['Blocks'] if block['BlockType'] == 'LINE'])
    return extracted_text.strip()

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

def ask_bedrock(prompt, model_id="meta.llama3-70b-instruct-v1:0"):
    payload = {
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.5
    }
    response = bedrock_runtime.invoke_model(
        body=json.dumps(payload),
        modelId=model_id,
        accept='application/json',
        contentType='application/json'
    )
    response_body = json.loads(response['body'].read())
    return response_body['generation']

def process_pdfs_and_answer_questions(pdf_directory, question):
    combined_text = extract_text_from_pdfs(pdf_directory)
    prompt = f"Context: {combined_text}\n\nQuestion: {question}\n\nAnswer:"
    return ask_bedrock(prompt)

if __name__ == "__main__":
    pdf_directory = "document-processing/Receipts/"
    question = "List of all companies invoice belongs to?"
    
    answer = process_pdfs_and_answer_questions(pdf_directory, question)
    print('\nQuestion:', question)
    print("\nAnswer:", answer)
