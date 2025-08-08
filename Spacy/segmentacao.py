import os
import json
import spacy
import zipfile

PASTA_SAIDA = "saida"
PASTA_SEGMENTACAO = os.path.join("saida_segmentada")
ARQUIVO_ZIP = os.path.join(PASTA_SEGMENTACAO, "segmentados.zip")
os.makedirs(PASTA_SEGMENTACAO, exist_ok=True)

try:
    nlp = spacy.load("pt_core_news_lg")
except OSError:
    raise RuntimeError("O modelo 'pt_core_news_lg' não está instalado. Use: python -m spacy download pt_core_news_lg")

def segmentar_texto(texto):   
    doc = nlp(texto)
    return [sent.text.strip() for sent in doc.sents]

def processar_arquivo_json(caminho_arquivo):
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        dados = json.load(f)

    dados_segmentados = {}
  
    for chave, valor in dados.items():
        if isinstance(valor, str):
            dados_segmentados[chave] = segmentar_texto(valor)
        else:
            dados_segmentados[chave] = valor 

    return dados_segmentados

def processar_todos_arquivos():
    arquivos_segmentados = []
    for arquivo in os.listdir(PASTA_SAIDA):
        if arquivo.lower().endswith(".json"):
            caminho_entrada = os.path.join(PASTA_SAIDA, arquivo)
            dados_segmentados = processar_arquivo_json(caminho_entrada)

            caminho_saida = os.path.join(PASTA_SEGMENTACAO, arquivo)
            with open(caminho_saida, "w", encoding="utf-8") as f:
                json.dump(dados_segmentados, f, ensure_ascii=False, indent=4)

    with zipfile.ZipFile(ARQUIVO_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for caminho in arquivos_segmentados:
            nome_arquivo = os.path.basename(caminho)
            zipf.write(caminho, arcname=nome_arquivo)
        
    print(f"\nTodos os arquivos segmentados foram compactados em: {ARQUIVO_ZIP}")
