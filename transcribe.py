
from faster_whisper import WhisperModel
from utils import format_time


def create_transcription(file_path, model_name):
    """
    Cria a transcrição de um arquivo de áudio usando um modelo Whisper.
    """
    print("Transcrição iniciada")
    # Time for model loading
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    
    # Time for transcription
    result = model.transcribe(file_path)
    segments, info = model.transcribe(file_path)
    
    detected_language = info.language
    return segments, detected_language
    

def write_srt(segments, srt_path):
    print(srt_path)
    print("Escrevendo arquivo SRT")
    # Time for SRT file writing
    with open(srt_path, 'w', encoding='utf-8') as srt_file:
        for i, segment in enumerate(segments):
            start = segment.start
            end = segment.end
            text = segment.text
            srt_file.write(f"{i+1}\n{format_time(start)} --> {format_time(end)}\n{text}\n\n")


