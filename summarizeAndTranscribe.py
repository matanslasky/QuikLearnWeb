import os
import whisper
import ffmpeg
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from transformers import pipeline

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Function to transcribe audio
def transcribe_audio(input_file, output_file):
    model = whisper.load_model("base")
    audio = whisper.load_audio(input_file)
    result = model.transcribe(audio)

    with open(output_file, "w", encoding='utf-8') as f:
        f.write(result["text"])

# Function to summarize text
def summarize_text(input_file, output_file):
    summarizer = pipeline("summarization")
    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()

    summary = summarizer(text, max_length=150, min_length=30, do_sample=False)
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(summary[0]['summary_text'])

# Check and convert to WAV
def process_file(file_path):
    if file_path.endswith(".mp3") or file_path.endswith(".mp4"):
        wav_file = os.path.splitext(file_path)[0] + ".wav"
        ffmpeg.input(file_path).output(wav_file).run()
        file_path = wav_file

    transcription_file = os.path.splitext(file_path)[0] + "_transcription.txt"
    transcribe_audio(file_path, transcription_file)

    return transcription_file

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))

    # Save file
    filepath = os.path.join('uploads', file.filename)
    file.save(filepath)

    # Process the file and summarize
    transcription_file = process_file(filepath)
    summary_file = 'summary.txt'
    summarize_text(transcription_file, summary_file)

    return send_file(summary_file, as_attachment=True)

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
