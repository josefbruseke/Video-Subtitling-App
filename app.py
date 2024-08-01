from flask import Flask, request, render_template, jsonify, send_from_directory
import whisper
import os
import subprocess

from file_processing import dividir_dicionario_em_chunks, ler_e_processar_arquivo_srt, reescrever_arquivo_srt, translate_chunks
from faster_whisper import WhisperModel
from utils import format_time, get_available_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def segments_to_dict(segments):
    srt_dict = {}
    for i, segment in enumerate(segments):
        start = segment.start
        end = segment.end
        text = segment.text
        srt_dict[i+1] = {
            "start": format_time(start),
            "end": format_time(end),
            "text": text
        }
    return srt_dict

def save_transcription(segments):
    srt_path = os.path.join(app.config['UPLOAD_FOLDER'], 'transcription.srt')
    with open(srt_path, 'w', encoding='utf-8') as srt_file:
        for i, segment in enumerate(segments):
            start = segment.start
            end = segment.end
            text = segment.text
            srt_file.write(f"{i+1}\n{format_time(start)} --> {format_time(end)}\n{text}\n\n")


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
    model_name = request.form['model']  # Alterado para 'model_name' para evitar conflito de nome
    if not idioma_selecionado:
        return jsonify({'error': 'Missing language inputs'}), 400
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        try:
            model = WhisperModel(model_name, device="cpu", compute_type="int8")
            result = model.transcribe(file_path)
            segments, _ = model.transcribe(file_path, )
            srt_path = os.path.join(app.config['UPLOAD_FOLDER'], 'transcription.srt')
            with open(srt_path, 'w', encoding='utf-8') as srt_file:
                for i, segment in enumerate(segments):
                    start = segment.start
                    end = segment.end
                    text = segment.text
                    srt_file.write(f"{i+1}\n{format_time(start)} --> {format_time(end)}\n{text}\n\n")

            tempos, textos = ler_e_processar_arquivo_srt(srt_path)
            tamanho_chunk = 20  
            textos_chunks = dividir_dicionario_em_chunks(textos, tamanho_chunk)
            texto_traduzido = translate_chunks(textos_chunks, target_language=idioma_selecionado)
            caminho_arquivo_traduzido = os.path.join(app.config['UPLOAD_FOLDER'], 'exemplo_traduzido.srt')
            reescrever_arquivo_srt(caminho_arquivo_traduzido, tempos, texto_traduzido)
            output_filename = 'video_traduzido.mp4'
            caminho_saida_video = os.path.join(app.config['UPLOAD_FOLDER'], get_available_filename(app.config['UPLOAD_FOLDER'], output_filename))
            print(caminho_saida_video)
            comando_ffmpeg = [
                'ffmpeg', '-i', file_path, '-vf', f"subtitles={caminho_arquivo_traduzido.replace(os.sep, '/')}", caminho_saida_video
            ]
            try:
                result = subprocess.run(comando_ffmpeg, check=True, capture_output=True, text=True)
                print("Saída do comando FFmpeg:", result.stdout)
            except subprocess.CalledProcessError as e:
                print("Erro ao executar o comando FFmpeg:", e.stderr)

            return jsonify({'success': 'File uploaded and translated successfully', 'output_file': os.path.basename(caminho_saida_video)})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
