import ast


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

def reescrever_arquivo_srt(caminho_arquivo, tempos, textos_traduzidos):
    # Converter a string textos_traduzidos em um dicionário
    try:
        textos = ast.literal_eval(textos_traduzidos)
    except (SyntaxError, ValueError) as e:
        print(f"Erro ao converter textos_traduzidos em um dicionário: {e}")
        return

    with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
        # Obter todos os IDs das legendas e ordená-los
        ids_legendas = sorted(tempos.keys())
        for numero_id in ids_legendas:
            # Escrever no arquivo o número da legenda, o tempo e o texto traduzido
            arquivo.write(f"{numero_id}\n{tempos[numero_id]}\n{textos[numero_id]}\n\n")
