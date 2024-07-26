from flask import Flask, request, render_template, jsonify, send_from_directory
from openai import OpenAI
from dotenv import load_dotenv
import whisper
import os
import re
import subprocess

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Obter a chave da API a partir das variáveis de ambiente
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def traduzir_texto(texto, idioma_entrada, idioma_destino):
    mensagem = f"Translate this text from {idioma_entrada} to {idioma_destino} maintaining cohesion and continuity between the sentences as if translating a continuous dialogue: {texto}"
    response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a translator."},
            {"role": "user", "content": mensagem},
        ],
        n=1,
        stop=None,
        temperature=0.3)
    traducao = response.choices[0].message.content.strip()
    return traducao

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

def extract_srt_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        srt_content = file.read()
    blocks = re.findall(r'(\d+\s*\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\s*\n.*?(?=\n\d|\Z))', srt_content, re.DOTALL)
    timestamps = []
    texts = []
    for block in blocks:
        timestamp = re.search(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', block).group()
        text = re.sub(r'\d+\s*\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\s*\n', '', block).strip()
        timestamps.append(timestamp)
        texts.append(text)
    return timestamps, texts

def combine_timestamps_and_texts(timestamps, translated_texts):
    srt_blocks = []
    for i in range(len(timestamps)):
        if i < len(translated_texts):
            srt_blocks.append(f"{i+1}\n{timestamps[i]}\n{translated_texts[i]}\n")
        else:
            srt_blocks.append(f"{i+1}\n{timestamps[i]}\n")
    return "\n".join(srt_blocks)

def format_time(seconds):
    millis = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)
    minutes = seconds // 60
    seconds = seconds % 60
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

if __name__ == '__main__':
    app.run(debug=True)
