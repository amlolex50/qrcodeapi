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


import os
import qrcode
import uuid
from flask import Flask, request, jsonify, url_for

app = Flask(__name__, static_folder='qrcodes')

@app.route('/generate_qrcode', methods=['POST'])
def generate_qrcode():
    try:
        data = request.json
        web_url = data['url']

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(web_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Ensure the directory exists
        qr_code_dir = 'qrcodes'
        os.makedirs(qr_code_dir, exist_ok=True)

        # Save the QR code
        unique_filename = f"{str(uuid.uuid4())}.png"
        file_path = os.path.join(qr_code_dir, unique_filename)
        img.save(file_path)

        # Build URL for QR code image and return it
        qr_code_url = request.url_root.rstrip('/') + url_for('static', filename=unique_filename)
        return jsonify({'qr_code_url': qr_code_url})
    
    except Exception as e:
        app.logger.error(f"Error generating QR code: {str(e)}", exc_info=True)
        return jsonify({'error': 'Error generating QR code'}), 500

