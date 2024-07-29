import os


def format_time(seconds):
    millis = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)
    minutes = seconds // 60
    seconds = seconds % 60
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

def get_available_filename(base_path, filename):
    # Extrai o nome do arquivo e a extensão
    name, ext = os.path.splitext(filename)
    counter = 0
    new_filename = filename
    
    # Incrementa o sufixo até encontrar um nome de arquivo disponível
    while os.path.exists(os.path.join(base_path, new_filename)):
        counter += 1
        new_filename = f"{name}({counter}){ext}"
    
    return new_filename