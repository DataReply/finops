import os
from dotenv import load_dotenv
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama.llms import OllamaLLM
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import textwrap

# Load environment variables
load_dotenv()

# ------------------------------
# CONFIGURATION
# ------------------------------
INPUT_FOLDER = "detailed_cvs"   # Folder containing PDFs
#OUTPUT_FOLDER_llama = "llama_summarized_cvs"  # Folder to save summarized PDFs
#OUTPUT_FOLDER_deepseek = "deepseek_summarized_cvs"  # Folder to save summarized PDFs
OUTPUT_FOLDER_mistral = "mistral_summarized_cvs"  # Folder to save summarized PDFs

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER_mistral, exist_ok=True)

# ------------------------------
# FUNCTION: Summarize PDF
# ------------------------------
def summarize_pdf(file_path):
    loader = PyPDFLoader(file_path)
    docs = loader.load_and_split()
    llm = OllamaLLM(model="mistral")  # Using LLaMA 3 with Ollama
    chain = load_summarize_chain(llm, chain_type='map_reduce')
    summary = chain.invoke(docs)
    
    return summary['output_text']  # Extract summary text

# ------------------------------
# FUNCTION: Save Text to PDF
# ------------------------------
def save_text_to_pdf(text, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica", 12)

    # Wrap text to fit within the page width
    wrapped_text = textwrap.wrap(text, width=90)
    
    y_position = 750  # Start position

    for line in wrapped_text:
        if y_position < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = 750
        c.drawString(50, y_position, line)
        y_position -= 20

    c.save()
    print(f"✅ Summarized CV saved to: {filename}")

# ------------------------------
# PROCESS ALL PDFs IN FOLDER
# ------------------------------
if __name__ == '__main__':
    for pdf_file in os.listdir(INPUT_FOLDER):
        if pdf_file.endswith(".pdf"):
            input_path = os.path.join(INPUT_FOLDER, pdf_file)
            output_path = os.path.join(OUTPUT_FOLDER_mistral, f"summary_{pdf_file}")

            print(f"📄 Processing CV from: {input_path}...")

            # Summarize PDF
            try:
                summary = summarize_pdf(input_path)
            except Exception as e:
                print(f"❌ Error summarizing {pdf_file}: {e}")
                continue

            # Save summary to PDF
            save_text_to_pdf(summary, output_path)

    print("✅✅✅ All PDFs processed successfully!")
