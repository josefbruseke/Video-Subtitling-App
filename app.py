from flask import Flask, request, render_template, jsonify, send_from_directory
from openai import OpenAI
from dotenv import load_dotenv
import whisper
import os
import re
import subprocess

from file_processing import ler_e_processar_arquivo_srt, reescrever_arquivo_srt
from translate import traduzir_texto
from utils import format_time


app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    idioma_entrada = request.form['idioma_entrada']
    idioma_destino = request.form['idioma_destino']
    if not idioma_entrada or not idioma_destino:
        return jsonify({'error': 'Missing language inputs'}), 400
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        try:
            model = whisper.load_model("medium")
            result = model.transcribe(file_path, language=idioma_entrada,)
            srt_path = os.path.join(app.config['UPLOAD_FOLDER'], 'transcription.srt')
            
            with open(srt_path, 'w', encoding='utf-8') as srt_file:
                for i, segment in enumerate(result['segments']):
                    start = segment['start']
                    end = segment['end']
                    text = segment['text']
                    srt_file.write(f"{i+1}\n{format_time(start)} --> {format_time(end)}\n{text}\n\n")

            timestamps, texts = extract_srt_data(srt_path)
            if not texts:
                return jsonify({'error': 'No text extracted from the transcription.'}), 500

            texto_para_traduzir = "\n\n".join(texts)
            traducao = traduzir_texto(texto_para_traduzir, idioma_entrada, idioma_destino)
            translated_texts = traducao.split('\n\n')
            novo_srt_conteudo = combine_timestamps_and_texts(timestamps, translated_texts)
            caminho_saida_srt = os.path.join(app.config['UPLOAD_FOLDER'], 'traducao.srt')
            with open(caminho_saida_srt, 'w', encoding='utf-8') as arquivo_saida:
                arquivo_saida.write(novo_srt_conteudo)

            caminho_saida_video = os.path.join(app.config['UPLOAD_FOLDER'], 'video_traduzido.mp4')
            comando_ffmpeg = [
                'ffmpeg', '-i', file_path, '-vf', f"subtitles={caminho_saida_srt.replace(os.sep, '/')}", caminho_saida_video
            ]
            subprocess.run(comando_ffmpeg, check=True, shell=True)

            return jsonify({'success': 'File uploaded and translated successfully', 'output_file': 'video_traduzido.mp4'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
