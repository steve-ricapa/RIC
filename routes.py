import os
import logging
from datetime import datetime
from flask import render_template, request, jsonify, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from app import app, db
from models import AudioAnalysis
from audio_processor import AudioProcessor
from ric_agent import RICAgent
import json

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg', 'flac'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with upload interface"""
    recent_analyses = AudioAnalysis.query.order_by(AudioAnalysis.upload_timestamp.desc()).limit(5).all()
    return render_template('index.html', recent_analyses=recent_analyses)

@app.route('/upload', methods=['POST'])
def upload_audio():
    """Handle audio file upload with educational context"""
    try:
        if 'audio_file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        file = request.files['audio_file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        if file.filename is None or not allowed_file(file.filename):
            flash('Invalid file format. Please upload MP3, WAV, M4A, OGG, or FLAC files.', 'error')
            return redirect(url_for('index'))
        
        # Save the file
        if file.filename is None:
            flash('Invalid filename', 'error')
            return redirect(url_for('index'))
        
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get educational context from form
        subject = request.form.get('subject', '').strip()
        grade_level = request.form.get('grade_level', '').strip()
        lesson_topic = request.form.get('lesson_topic', '').strip()
        additional_context = request.form.get('additional_context', '').strip()
        
        # Create database record
        analysis = AudioAnalysis()
        analysis.filename = filename
        analysis.original_filename = file.filename
        analysis.subject = subject
        analysis.grade_level = grade_level
        analysis.lesson_topic = lesson_topic
        analysis.additional_context = additional_context
        analysis.status = 'uploaded'
        db.session.add(analysis)
        db.session.commit()
        
        flash('File uploaded successfully! Analysis is starting...', 'success')
        return redirect(url_for('analyze', analysis_id=analysis.id))
        
    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        flash('Error uploading file. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/analyze/<int:analysis_id>')
def analyze(analysis_id):
    """Display analysis page and trigger processing"""
    analysis = AudioAnalysis.query.get_or_404(analysis_id)
    
    # If not yet processed, start processing
    if analysis.status == 'uploaded':
        try:
            process_audio_analysis(analysis)
        except Exception as e:
            logging.error(f"Analysis error: {str(e)}")
            analysis.status = 'error'
            analysis.error_message = str(e)
            db.session.commit()
    
    return render_template('analysis.html', analysis=analysis)

@app.route('/api/analysis/<int:analysis_id>/status')
def get_analysis_status(analysis_id):
    """Get current analysis status via API"""
    analysis = AudioAnalysis.query.get_or_404(analysis_id)
    return jsonify({
        'status': analysis.status,
        'error_message': analysis.error_message
    })

@app.route('/api/analysis/<int:analysis_id>/results')
def get_analysis_results(analysis_id):
    """Get analysis results via API"""
    analysis = AudioAnalysis.query.get_or_404(analysis_id)
    
    if analysis.status != 'completed':
        return jsonify({'error': 'Analysis not completed'}), 400
    
    return jsonify({
        'transcription': analysis.get_transcription_data(),
        'prosody': analysis.get_prosody_data(),
        'feedback': analysis.get_ric_feedback()
    })

@app.route('/history')
def history():
    """View analysis history"""
    analyses = AudioAnalysis.query.order_by(AudioAnalysis.upload_timestamp.desc()).all()
    return render_template('history.html', analyses=analyses)

def process_audio_analysis(analysis):
    """Process audio file and generate analysis"""
    try:
        analysis.status = 'processing'
        db.session.commit()
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], analysis.filename)
        
        # Initialize processors
        audio_processor = AudioProcessor()
        ric_agent = RICAgent()
        
        logging.info(f"Starting transcription for {analysis.filename}")
        
        # Step 1: Transcribe audio
        transcription_result = audio_processor.transcribe_audio(filepath)
        analysis.transcription_text = transcription_result['text']
        analysis.set_transcription_data(transcription_result)
        db.session.commit()
        
        logging.info(f"Starting prosodic analysis for {analysis.filename}")
        
        # Step 2: Analyze prosody
        prosody_result = audio_processor.analyze_prosody(filepath)
        analysis.set_prosody_data(prosody_result)
        db.session.commit()
        
        logging.info(f"Starting RIC feedback generation for {analysis.filename}")
        
        # Step 3: Generate RIC feedback with educational context
        educational_context = analysis.get_educational_context()
        combined_data = {
            'transcription': transcription_result,
            'prosody': prosody_result,
            'educational_context': educational_context
        }
        
        feedback = ric_agent.generate_educational_feedback(combined_data)
        analysis.set_ric_feedback(feedback)
        
        # Mark as completed
        analysis.status = 'completed'
        analysis.analysis_timestamp = datetime.utcnow()
        db.session.commit()
        
        logging.info(f"Analysis completed for {analysis.filename}")
        
    except Exception as e:
        logging.error(f"Processing error for {analysis.filename}: {str(e)}")
        analysis.status = 'error'
        analysis.error_message = str(e)
        db.session.commit()
        raise e
