import os

def count_pdfs(directory):
    pdf_count = 0

    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(directory):
        for file in files:
#            if file.lower().endswith('.pdf'):
                pdf_count += 1

    return pdf_count

# Specify the directory to search
directory_path = "document-processing/Receipts/"

# Count PDFs
pdf_count = count_pdfs(directory_path)
print(f"Total PDF files: {pdf_count}")