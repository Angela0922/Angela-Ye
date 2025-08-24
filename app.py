from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
import uuid
from dotenv import load_dotenv
from video_processor import VideoProcessor
from translation_service import TranslationService
from makeup_transformer import MakeupTransformer
import threading
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 104857600))  # 100MB
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['OUTPUT_FOLDER'] = os.getenv('OUTPUT_FOLDER', 'outputs')

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Initialize services
video_processor = VideoProcessor()
translation_service = TranslationService()
makeup_transformer = MakeupTransformer()

# Store processing status
processing_status = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Generate unique ID for this processing job
        job_id = str(uuid.uuid4())
        
        # Save uploaded file
        filename = f"{job_id}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Start processing in background
        processing_status[job_id] = {
            'status': 'started',
            'progress': 0,
            'message': 'Processing started...'
        }
        
        thread = threading.Thread(
            target=process_video_async,
            args=(job_id, filepath)
        )
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'message': 'Video uploaded successfully. Processing started.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status/<job_id>')
def get_status(job_id):
    if job_id not in processing_status:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(processing_status[job_id])

@app.route('/download/<job_id>')
def download_result(job_id):
    try:
        if job_id not in processing_status:
            return jsonify({'error': 'Job not found'}), 404
        
        status = processing_status[job_id]
        if status['status'] != 'completed':
            return jsonify({'error': 'Processing not completed'}), 400
        
        output_path = status.get('output_path')
        if not output_path or not os.path.exists(output_path):
            return jsonify({'error': 'Output file not found'}), 404
        
        return send_file(output_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_video_async(job_id, input_path):
    try:
        # Update status
        processing_status[job_id].update({
            'status': 'processing',
            'progress': 10,
            'message': 'Extracting audio and analyzing video...'
        })
        
        # Step 1: Extract audio and get video info
        audio_path, video_info = video_processor.extract_audio(input_path)
        
        processing_status[job_id].update({
            'progress': 25,
            'message': 'Transcribing and translating audio...'
        })
        
        # Step 2: Transcribe and translate audio
        spanish_text = translation_service.transcribe_audio(audio_path)
        english_text = translation_service.translate_text(spanish_text)
        
        processing_status[job_id].update({
            'progress': 40,
            'message': 'Generating English audio...'
        })
        
        # Step 3: Generate English TTS
        english_audio_path = translation_service.text_to_speech(english_text, job_id)
        
        processing_status[job_id].update({
            'progress': 55,
            'message': 'Processing video frames and transforming makeup...'
        })
        
        # Step 4: Process video frames and transform makeup
        transformed_video_path = makeup_transformer.transform_video(input_path, job_id)
        
        processing_status[job_id].update({
            'progress': 80,
            'message': 'Combining transformed video with translated audio...'
        })
        
        # Step 5: Combine transformed video with new audio
        output_path = video_processor.combine_video_audio(
            transformed_video_path, 
            english_audio_path, 
            job_id
        )
        
        processing_status[job_id].update({
            'status': 'completed',
            'progress': 100,
            'message': 'Processing completed successfully!',
            'output_path': output_path
        })
        
    except Exception as e:
        processing_status[job_id].update({
            'status': 'error',
            'message': f'Error: {str(e)}'
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)