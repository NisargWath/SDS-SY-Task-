from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
import google.generativeai as genai
import markdown
from pdf_processor import get_pdf_answer

app = Flask(__name__)

# Set UPLOAD_FOLDER to the absolute path where the PDF file is located
app.config['UPLOAD_FOLDER'] = '/Users/appleApple/Desktop/SDS/Code'

# Configure API key for Generative AI
GOOGLE_API_KEY = "AIzaSyCpDjrKq5lkm3LaW_U3N53IvNbHc4h5cnA"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name="gemini-pro")

def to_markdown(text):
    # Convert plain text to Markdown format
    md = markdown.markdown(text)
    return md

def create_table():
    conn = sqlite3.connect('college.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            dob TEXT NOT NULL,
            mobile_no TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_user(username, password, email, dob, mobile_no):
    conn = sqlite3.connect('college.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, password, email, dob, mobile_no)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, password, email, dob, mobile_no))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('signup.html')


@app.route('/scholorship')
def scholorship():
    return render_template('scholorship.html')
@app.route('/Document')
def Document():
    return render_template('Document.html')
@app.route('/Fees')
def Fees():
    return render_template('Fees.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['UserName']
    password = request.form['Password']
    email = request.form['emailPrefix'] + '@coeptech.ac.in'
    dob = request.form['DOB']
    mobile_no = request.form['MobileNo']

    # Check if user already exists
    conn = sqlite3.connect('college.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE username = ? OR email = ?
    ''', (username, email))
    existing_user = cursor.fetchone()  
    conn.close()

    if existing_user:
        return render_template('users.html')
    else:
        insert_user(username, password, email, dob, mobile_no)
        return redirect(url_for('users'))  

@app.route('/users')
def users():
    conn = sqlite3.connect('college.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    user_list = cursor.fetchall()
    conn.close()
    return render_template('users.html', users=user_list)

@app.route('/send_message', methods=['POST'])
def send_message_cost():
    try:
        # Retrieve the message and append word limit request
        question = request.form['message'] + " in 100-150 words related to COEP Engineering college scholorship for students if you don't find answer in pdf give on your own"
        print("Question generated:", question)

        # Define the path to the PDF file
        pdf_file = os.path.join(app.config['UPLOAD_FOLDER'], 'Untitled.pdf')
        
        # Check if the file exists
        if not os.path.exists(pdf_file):
            return jsonify({"error": "PDF file not found."}), 404
        
        # Process the PDF file and retrieve the answer
        result = get_pdf_answer(pdf_file, question)
        print("Result from PDF processing:", result)
        
        # Extract and convert the output text to markdown
        output_text = result.get('output_text', 'No answer found.')
        
        # Return the processed message as JSON
        return jsonify({"message": to_markdown(output_text)})
    
    except Exception as e:
        print("Error occurred:",