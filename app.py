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
    idioma_selecionado = request.form['idioma_destino']
    model = request.form['model']
    if not idioma_selecionado:
        return jsonify({'error': 'Missing language inputs'}), 400
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        try:
            model = whisper.load_model(model)
            result = model.transcribe(file_path)
            idioma_detectado = result['language'] 
            srt_path = os.path.join(app.config['UPLOAD_FOLDER'], 'transcription.srt')
            with open(srt_path, 'w', encoding='utf-8') as srt_file:
                for i, segment in enumerate(result['segments']):
                    start = segment['start']
                    end = segment['end']
                    text = segment['text']
                    srt_file.write(f"{i+1}\n{format_time(start)} --> {format_time(end)}\n{text}\n\n")

            legendas = ler_e_processar_arquivo_srt(srt_path)
            # Traduzir o texto das legendas
            print(legendas)
            for legenda in legendas:
                print()
                print(legenda)
                legenda['texto'] = traduzir_texto(legenda['texto'], idioma_entrada=idioma_detectado,   idioma_destino=idioma_selecionado)
            # Reescrever o arquivo SRT com as legendas traduzidas
            print(legendas)
            caminho_arquivo_traduzido = 'uploads/exemplo_traduzido.srt'
            reescrever_arquivo_srt(caminho_arquivo_traduzido, legendas)
            print(f"Arquivo traduzido salvo como {caminho_arquivo_traduzido}")
            caminho_saida_video = os.path.join(app.config['UPLOAD_FOLDER'], 'video_traduzido.mp4')
            comando_ffmpeg = [
                'ffmpeg', '-i', file_path, '-vf', f"subtitles={caminho_arquivo_traduzido.replace(os.sep, '/')}", caminho_saida_video
            ]
            try:
                result = subprocess.run(comando_ffmpeg, check=True, capture_output=True, text=True)
                print("Saída do comando FFmpeg:", result.stdout)
            except subprocess.CalledProcessError as e:
                print("Erro ao executar o comando FFmpeg:", e.stderr)

            return jsonify({'success': 'File uploaded and translated successfully', 'output_file': 'video_traduzido.mp4'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
