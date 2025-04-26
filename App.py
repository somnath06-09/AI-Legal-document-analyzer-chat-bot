import google.generativeai as genai
import sqlite3
import logging
from flask import Flask, request, jsonify
from Database import store_analysis, fetch_recent_analyses
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from Gemini_helper import get_gemini_response

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Replace with your actual Gemini API key
API_KEY = "AIzaSyBPbcjoiIi-KoaVbHjhCZbt7STepvmsEUQ"

# Configure Gemini API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro-latest")

UPLOAD_FOLDER = 'uploaded_documents'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ Route to Ask Gemini & Store Chat
@app.route('/ask_gemini', methods=['POST'])
def ask_gemini():
    try:
        # Get user input
        user_input = request.json.get("message", "")
        logger.info(f"Received user input: {user_input}")

        if not user_input:
            logger.warning("No message provided.")
            return jsonify({"error": "No message provided"}), 400

        # Send message to Gemini API
        response = model.generate_content(user_input)
        formatted_response = response.text.replace("**", "<strong>").replace("**", "</strong>").replace("* ", "<br>• ").replace("\n", "<br>")
        bot_reply = (
            "<div style='font-family:Arial,sans-serif;line-height:1.6;font-size:16px;color:#333;'>"
            f"<strong>AI:</strong> {formatted_response}"
            "</div>"
        )
        logger.info(f"Gemini API response: {bot_reply}")

        # Store chat in SQLite database
        with sqlite3.connect("chatbot.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO chat_history (user_message, bot_response) VALUES (?, ?)",
                           (user_input, bot_reply))
            conn.commit()
        logger.info(f"Stored chat history for user message: {user_input}")

        return jsonify({"response": bot_reply})

    except Exception as e:
        logger.error(f"Error in '/ask_gemini' route: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ Analyze Document
@app.route('/analyze_file', methods=['POST'])
def analyze_document():
    try:
        if 'file' not in request.files:
            logger.warning("No file part in the request.")
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        if file.filename == '':
            logger.warning("Empty filename in upload.")
            return jsonify({"error": "No file selected"}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            logger.info(f"Saved file to {file_path}")

            # Process with Gemini
            logger.info(f"Sending {file_path} to Gemini helper.")
            bot_reply = get_gemini_response(file_path)
            logger.info(f"Received bot reply: {bot_reply}")

            if not bot_reply:
                bot_reply = "Gemini did not return any output. Please check the document content."

            # Store in DB
            with sqlite3.connect("chatbot.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO chat_history (user_message, bot_response) VALUES (?, ?)",
                               (f"[Document: {filename}]", bot_reply))
                conn.commit()
            logger.info("Stored document analysis result in database.")

            return jsonify({"response": bot_reply})

        else:
            logger.warning("Unsupported file type.")
            return jsonify({"error": "Unsupported file type"}), 400

    except Exception as e:
        logger.exception("Exception occurred while analyzing document.")
        return jsonify({"error": f"Something went wrong during document analysis: {str(e)}"}), 500

# ✅ Retrieve Chat History
@app.route('/chat_history', methods=['GET'])
def chat_history():
    try:
        logger.info("Fetching chat history.")
        with sqlite3.connect("chatbot.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_message, bot_response FROM chat_history ORDER BY id DESC LIMIT 10")
            history = cursor.fetchall()

        if history:
            chat_data = [{"user": msg, "bot": res} for msg, res in history]
            logger.info(f"Retrieved {len(history)} chat records.")
            return jsonify({"history": chat_data})
        else:
            logger.warning("No chat history found.")
            return jsonify({"history": []})

    except Exception as e:
        logger.error(f"Error in '/chat_history' route: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ Initialize DB on Startup
if __name__ == '__main__':
    from Database import store_analysis, fetch_recent_analyses
    app.run(debug=True)