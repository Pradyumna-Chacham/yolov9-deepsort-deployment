from flask import Flask, request, redirect, url_for, render_template, send_from_directory, send_file, jsonify
from flask_lambda import FlaskLambda
app = FlaskLambda(__name__)

import os
import glob
from werkzeug.utils import secure_filename
from detect_dual_tracking import run, parse_opt

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}
STATUS_FILE = 'status.txt'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    video_path = None
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            status = f.read().strip()
        if status.startswith("Processing completed:"):
            video_path = status.split(": ", 1)[1]
    return render_template('index.html', video_path=video_path)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # Process the video immediately and return the download link
        return process_video(input_path)

@app.route('/progress_status')
def progress_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            status = f.read().strip()
        return jsonify(status=status)
    return jsonify(status="No status available.")

@app.route('/results/<folder>/<filename>')
def processed_file(folder, filename):
    return send_from_directory(os.path.join(app.config['PROCESSED_FOLDER'], folder), filename)

@app.route('/video/<path:video_path>')
def serve_video(video_path):
    return send_file(os.path.join(app.config['PROCESSED_FOLDER'], video_path), mimetype='video/mp4')

@app.route('/download/<path:video_path>')
def download_video(video_path):
    return send_file(os.path.join(app.config['PROCESSED_FOLDER'], video_path), as_attachment=True)

def update_status(message):
    with open(STATUS_FILE, 'w') as f:
        f.write(message)

def process_video(input_path):
    opt = parse_opt()
    opt.source = input_path
    update_status("Processing started")
    run(**vars(opt))
    
    # Find the latest exp folder
    exp_folders = glob.glob(os.path.join(PROCESSED_FOLDER, 'exp*'))
    latest_exp_folder = max(exp_folders, key=os.path.getmtime)
    
    # Find the video file in the latest exp folder
    video_files = glob.glob(os.path.join(latest_exp_folder, '*.mp4'))
    if video_files:
        latest_video = max(video_files, key=os.path.getmtime)
        video_filename = os.path.basename(latest_video)
        video_path = f"{os.path.basename(latest_exp_folder)}/{video_filename}"
        update_status("Processing completed: " + video_path)
        return download_video(video_path)
    else:
        update_status("No video file found in the latest experiment folder.")
        return "No video file found in the latest experiment folder.", 500

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    app.run(debug=True)
