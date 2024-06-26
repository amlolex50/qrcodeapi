# app.py
import subprocess
import uuid
from flask import Flask, request, jsonify, send_file
import requests
from werkzeug.utils import secure_filename
import os
import ffmpeg
from scipy.spatial import distance


def create_app():
    app = Flask(__name__, static_folder='uploads', static_url_path='/uploads')
    app.config['UPLOAD_FOLDER'] = '/app/uploads/'
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    # Other setup code...
    return app


app = create_app()


@app.route('/', methods=['GET'])
def homepage():
    return "Homepage"


@app.route('/hello', methods=['GET'])
def hello():
    return "Hello"

@app.route('/get_similar', methods=['POST'])
def cosine_similarity():
    data = request.json
    query_vector = data['query_vector']
    vector_text_pairs = data['vectors']

    # Extract embeddings and their corresponding texts
    vectors = [pair['embeddings'] for pair in vector_text_pairs]
    texts = [pair['text'] for pair in vector_text_pairs]

    # Calculate cosine similarity for each vector
    # Return the index of the most similar vector
    most_similar_index = max(range(len(vectors)), key=lambda index: 1 - distance.cosine(query_vector, vectors[index]))

    return jsonify({'most_similar_text': texts[most_similar_index]})


from flask import Flask, request, send_file, jsonify
import fitz  # PyMuPDF
import io
import os
from docx import Document
from docx.shared import RGBColor


def redact_pdf(file, keywords):
    document = fitz.open(stream=file.read(), filetype="pdf")
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        for keyword in keywords:
            areas = page.search_for(keyword)
            for area in areas:
                rect = fitz.Rect(area)
                page.draw_rect(rect, color=(0, 0, 0), fill=(0, 0, 0))
    redacted_pdf = io.BytesIO()
    document.save(redacted_pdf)
    redacted_pdf.seek(0)
    return redacted_pdf

def redact_docx(file, keywords):
    document = Document(file)
    for paragraph in document.paragraphs:
        for keyword in keywords:
            if keyword in paragraph.text:
                inline = paragraph.runs
                for i in range(len(inline)):
                    if keyword in inline[i].text:
                        inline[i].text = inline[i].text.replace(keyword, "█" * len(keyword))

    redacted_docx = io.BytesIO()
    document.save(redacted_docx)
    redacted_docx.seek(0)
    return redacted_docx

@app.route('/redact', methods=['POST'])
def redact():
    try:
        keywords = request.form.getlist('keywords')
        if not keywords:
            return jsonify({'error': 'No keywords provided'}), 400

        file = request.files.get('file')
        if file is None:
            return jsonify({'error': 'No file provided'}), 400

        filename = file.filename
        if filename.endswith('.pdf'):
            redacted_file = redact_pdf(file, keywords)
            return send_file(redacted_file, attachment_filename='redacted.pdf', as_attachment=True)
        elif filename.endswith('.docx'):
            redacted_file = redact_docx(file, keywords)
            return send_file(redacted_file, attachment_filename='redacted.docx', as_attachment=True)
        else:
            return jsonify({'error': 'Unsupported file type. Only PDF and DOCX are supported.'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'error': 'Internal server error'}), 500






