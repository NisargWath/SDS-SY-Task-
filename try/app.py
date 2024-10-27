from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import markdown

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
DATABASE = 'document_data.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Gemini model for the chatbot


# Helper to convert text to markdown
def to_markdown(text):
    return markdown.markdown(text)

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Create the table if not exists
def initialize_database():
    with get_db_connection() as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            filename TEXT NOT NULL
        )
        ''')
        conn.commit()

initialize_database()

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_document():
    if 'document' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['document']
    username = request.form.get('username')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Store file and username in the database
    with get_db_connection() as conn:
        conn.execute('INSERT INTO documents (username, filename) VALUES (?, ?)', (username, filename))
        conn.commit()

    return jsonify({"message": "File uploaded successfully", "filename": filename})

@app.route('/chat', methods=['POST'])
def chat():
    username = request.form['username']
    question = request.form['question']

    # Retrieve filename for the user
    conn = get_db_connection()
    cursor = conn.execute('SELECT filename FROM documents WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "No document found for the user."}), 404

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], row['filename'])

    # Question processing with Gemini
    message = HumanMessage(
        content=[
            {"type": "text", "text": f"{question}"},
            {"type": "document", "filename": file_path}
        ]
    )
    
    # Invoke the Gemini model and get response
    try:
        result = llm.invoke([message])
        response_text = result.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"response": to_markdown(response_text)})

if __name__ == "__main__":
    app.run(debug=True, port=8000)
