
# Função para ler e processar o arquivo SRT
def ler_e_processar_arquivo_srt(caminho_arquivo):
    print('ler e processar iniciado')
    print(caminho_arquivo)
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        conteudo = arquivo.read()
    
    legendas = []
    blocos = conteudo.strip().split('\n\n')
    
    for bloco in blocos:
        linhas = bloco.split('\n')
        numero_legenda = int(linhas[0])
        tempo = linhas[1]
        texto = " ".join(linhas[2:])
        legendas.append({
            "numero": numero_legenda,
            "tempo": tempo,
            "texto": texto
        })
    print('ler e processar finalizado')

    return legendas


# Função para reescrever o arquivo SRT com as legendas traduzidas
def reescrever_arquivo_srt(caminho_arquivo, legendas):
    print('reescrever inciado')
    with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
        for legenda in legendas:
            arquivo.write(f"{legenda['numero']}\n")
            arquivo.write(f"{legenda['tempo']}\n")
            arquivo.write(f"{legenda['texto']}\n\n")
