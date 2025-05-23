from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import subprocess
import time  # Add time module for measuring execution time


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
    start_total = time.time()
    
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
        # Time for file saving
        start_save = time.time()
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        save_time = time.time() - start_save
        
        try:
            print("Transcrição iniciada")
            # Time for model loading
            start_model_load = time.time()
            model = WhisperModel(model_name, device="cpu", compute_type="int8")
            model_load_time = time.time() - start_model_load
            print(f"Modelo carregado em {model_load_time:.2f} segundos")
            
            # Time for transcription
            start_transcription = time.time()
            result = model.transcribe(file_path)
            segments, info = model.transcribe(file_path)
            transcription_time = time.time() - start_transcription
            
            detected_language = info.language
            print(f"Detected language '{info.language}' with probability {info.language_probability} in {transcription_time:.2f} seconds")
            
            # Time for SRT file writing
            start_srt_write = time.time()
            srt_path = os.path.join(app.config['UPLOAD_FOLDER'], 'transcription.srt')
            with open(srt_path, 'w', encoding='utf-8') as srt_file:
                for i, segment in enumerate(segments):
                    start = segment.start
                    end = segment.end
                    text = segment.text
                    srt_file.write(f"{i+1}\n{format_time(start)} --> {format_time(end)}\n{text}\n\n")
            srt_write_time = time.time() - start_srt_write

            # Time for SRT processing
            start_srt_process = time.time()
            tempos, textos = ler_e_processar_arquivo_srt(srt_path)
            srt_process_time = time.time() - start_srt_process

            # Time for chunking
            start_chunking = time.time()
            tamanho_chunk = 20  
            textos_chunks = dividir_dicionario_em_chunks(textos, tamanho_chunk)
            chunking_time = time.time() - start_chunking

            # Time for translation
            start_translation = time.time()
            texto_traduzido = translate_chunks(textos_chunks, target_language=idioma_selecionado, origin_language=detected_language)
            translation_time = time.time() - start_translation

            # Time for writing translated SRT
            start_write_translated = time.time()
            caminho_arquivo_traduzido = os.path.join(app.config['UPLOAD_FOLDER'], 'exemplo_traduzido.srt')
            reescrever_arquivo_srt(caminho_arquivo_traduzido, tempos, texto_traduzido)
            write_translated_time = time.time() - start_write_translated

            # Time for video processing with FFmpeg
            start_ffmpeg = time.time()
            output_filename = 'video_traduzido.mp4'
            caminho_saida_video = os.path.join(app.config['UPLOAD_FOLDER'], get_available_filename(app.config['UPLOAD_FOLDER'], output_filename))
            print(caminho_saida_video)
            comando_ffmpeg = [
                'ffmpeg', '-i', file_path, '-vf', f"subtitles={caminho_arquivo_traduzido.replace(os.sep, '/')}", caminho_saida_video
            ]
            try:
                result = subprocess.run(comando_ffmpeg, check=True, capture_output=True, text=True)
                ffmpeg_time = time.time() - start_ffmpeg
                print(f"FFmpeg processing completed in {ffmpeg_time:.2f} seconds")
            except subprocess.CalledProcessError as e:
                ffmpeg_time = time.time() - start_ffmpeg
                print(f"Erro ao executar o comando FFmpeg após {ffmpeg_time:.2f} segundos:", e.stderr)

            # Calculate total time
            total_time = time.time() - start_total
            
            # Print summary of timing
            print(f"\nPerformance Summary:")
            print(f"File save: {save_time:.2f} seconds")
            print(f"Model loading: {model_load_time:.2f} seconds")
            print(f"Transcription: {transcription_time:.2f} seconds")
            print(f"SRT writing: {srt_write_time:.2f} seconds")
            print(f"SRT processing: {srt_process_time:.2f} seconds")
            print(f"Text chunking: {chunking_time:.2f} seconds")
            print(f"Translation: {translation_time:.2f} seconds")
            print(f"Writing translated SRT: {write_translated_time:.2f} seconds")
            print(f"FFmpeg processing: {ffmpeg_time:.2f} seconds")
            print(f"Total processing time: {total_time:.2f} seconds\n")

            return jsonify({
                'success': 'File uploaded and translated successfully', 
                'output_file': os.path.basename(caminho_saida_video),
                'timing': {
                    'file_save': round(save_time, 2),
                    'model_load': round(model_load_time, 2),
                    'transcription': round(transcription_time, 2),
                    'srt_writing': round(srt_write_time, 2),
                    'srt_processing': round(srt_process_time, 2),
                    'text_chunking': round(chunking_time, 2),
                    'translation': round(translation_time, 2),
                    'writing_translated': round(write_translated_time, 2),
                    'ffmpeg_processing': round(ffmpeg_time, 2),
                    'total': round(total_time, 2)
                }
            })
        except Exception as e:
            total_time = time.time() - start_total
            print(f"Error occurred after {total_time:.2f} seconds: {str(e)}")
            return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
