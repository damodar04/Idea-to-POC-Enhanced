from pypdf import PdfReader
import sys

# Force utf-8 output for console
sys.stdout.reconfigure(encoding='utf-8')

try:
    reader = PdfReader("d:/Idea_to_POC-main/Idea_to_POC-main/IDEA_to_POC.pdf")
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    with open("pdf_content_utf8.txt", "w", encoding="utf-8") as f:
        f.write(text)
        
    print("PDF Content Extracted to pdf_content_utf8.txt")
except Exception as e:
    print(f"Failed to read PDF: {e}")
