import google.generativeai as genai
from PyPDF2 import PdfReader

# Set your API key
genai.configure(api_key="YOUR_API_KEY")

# ✅ Use the correct model
model = genai.GenerativeModel("gemini-1.5-pro-latest")

def get_gemini_response(file_path):
    try:
        # Read text from PDF or TXT
        text = ""
        if file_path.endswith(".pdf"):
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""

        elif file_path.endswith(".txt"):
            with open(file_path, 'r') as f:
                text = f.read()

        if not text.strip():
            return "The uploaded document doesn't contain readable text."

        # Gemini prompt
        prompt = f"Analyze this legal document and summarize its key points:\n\n{text[:30000]}"

        # Use Gemini to generate content
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        print("Error from Gemini_helper.py:", e)
        return "I'm sorry, something went wrong while processing the request."
