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
llm = ChatGoogleGenerativeAI(model="gemini-pro")

# Helper to convert text to markdown
def to_markdown(text):
    return markdown.markdown(text)

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

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

    # Store file and username in the database with 'Pending' status
    with get_db_connection() as conn:
        conn.execute('INSERT INTO documents (username, filename, status) VALUES (?, ?, ?)', (username, filename, 'Pending'))
        conn.commit()

    return jsonify({"message": "File uploaded successfully and pending admin review.", "filename": filename})

@app.route('/admin', methods=['GET'])
def admin_dashboard():
    # Retrieve all uploaded documents with their statuses
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM documents')
    documents = cursor.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', documents=documents)

@app.route('/admin/approve/<int:doc_id>', methods=['POST'])
def approve_document(doc_id):
    # Update document status to 'Approved'
    with get_db_connection() as conn:
        conn.execute('UPDATE documents SET status = ? WHERE id = ?', ('Approved', doc_id))
        conn.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject/<int:doc_id>', methods=['POST'])
def reject_document(doc_id):
    # Update document status to 'Rejected'
    with get_db_connection() as conn:
        conn.execute('UPDATE documents SET status = ? WHERE id = ?', ('Rejected', doc_id))
        conn.commit()
    return redirect(url_for('admin_dashboard'))
 
if __name__ == "__main__":
    app.run(debug=True)
