import ast
import json
import re


from translate import traduzir_texto  # Supondo que você tenha uma função traduzir_texto disponível

def ler_e_processar_arquivo_srt(caminho_arquivo):
    print('ler e processar iniciado')
    print(caminho_arquivo)
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        conteudo = arquivo.read()

    tempos = {}
    textos = {}
    blocos = conteudo.strip().split('\n\n')
    
    for bloco in blocos:
        linhas = bloco.split('\n')
        numero_id = int(linhas[0])
        tempo = linhas[1]
        texto = " ".join(linhas[2:])
        tempos[numero_id] = tempo
        textos[numero_id] = texto
    print('ler e processar finalizado')


    return tempos, textos

def reescrever_arquivo_srt(caminho_arquivo, tempos, textos):
    print('reescrever arquivo srt iniciado')
    try:
        with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
            # Obter todos os IDs das legendas e ordená-los
            ids_legendas = sorted(tempos.keys(), key=int)
            for numero_id in ids_legendas:
                try:
                    # Verificar se o número da legenda, tempo e texto estão presentes
                    if numero_id not in tempos or numero_id not in textos:
                        print(f"Dados ausentes para o ID {numero_id}")
                        continue
                        
                    # Verificar se o tempo e o texto não estão vazios
                    if not tempos[numero_id] or not textos[numero_id]:
                        print(f"Tempo ou texto ausente para o ID {numero_id}")
                        continue
                        
                    # Escrever no arquivo o número da legenda, o tempo e o texto traduzido
                    arquivo.write(f"{numero_id}\n{tempos[numero_id]}\n{textos[numero_id]}\n\n")
                except Exception as e:
                    print(f"Erro ao processar ID {numero_id}: {e}")
    except Exception as e:
        print(f"Erro ao abrir o arquivo: {e}")
    print(f"Arquivo traduzido salvo como {caminho_arquivo}")



# Função para dividir o dicionário em chunks
def dividir_dicionario_em_chunks(dicionario, tamanho_chunk):
    if not dicionario:
        return []
    
    iterador = iter(dicionario.items())
    chunks = []
    
    while True:
        chunk = dict()
        for _ in range(tamanho_chunk):
            try:
                chave, valor = next(iterador)
                chunk[chave] = valor
            except StopIteration:
                if chunk:
                    chunks.append(chunk)
                return chunks

        chunks.append(chunk)

def dict_filter(text):
    start = text.find("{")
    end = text.rfind("}") + 1

    if start != -1 and end != -1:
        dictionary_text = text[start:end]
    else:
        print("Nenhum dicionário encontrado no texto.")
    dictionary_text = eval(dictionary_text)
    return dictionary_text

def translate_chunks(textos_chunks, target_language):
    textos_traduzidos = {}

    for chunk in textos_chunks:
        chunk_traduzido_dict = dict_filter(traduzir_texto(idioma_destino=target_language, texto=chunk))
        print(type(chunk_traduzido_dict))
        print(f'Chunk traduzido: {chunk_traduzido_dict}')
        textos_traduzidos.update(chunk_traduzido_dict)
    return textos_traduzidos