import os
import json
import zipfile
import re
import pandas as pd
from tqdm import tqdm
from transformers import pipeline

PASTA_SEGMENTADA = "saida_segmentada"
PASTA_DATASETS = "datasets"
os.makedirs(PASTA_DATASETS, exist_ok=True)

def extrair_arquivos_segmentados():
    """Extrai os arquivos segmentados do ZIP para a pasta de segmentação."""
    if os.path.exists(ARQUIVO_ZIP):
        try:
            with zipfile.ZipFile(ARQUIVO_ZIP, 'r') as zip_ref:
                zip_ref.extractall(PASTA_SEGMENTADA)
            print(f"Arquivos extraídos para: {PASTA_SEGMENTADA}")
        except Exception as e:
            print(f"Erro ao extrair {ARQUIVO_ZIP}: {e}")
    else:
        print(f"Arquivo {ARQUIVO_ZIP} não encontrado.")

def classificar_efeitos_bulas():
    # Carregar os rótulos
    try:
        with open("rotulos.json", encoding="utf-8") as f:
            efeitos = json.load(f)
    except Exception as e:
        print(f"Erro ao carregar rotulos.json: {e}")
        return

    try:
        classifier = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli")
        arquivos_json = [arq for arq in os.listdir(PASTA_SEGMENTADA) if arq.endswith(".json")]
    except Exception as e:
        print(f"Erro ao carregar modelo de classificação: {e}")
        return

    for arquivo in arquivos_json:
        try:
            caminho = os.path.join(PASTA_SEGMENTADA, arquivo)
            with open(caminho, encoding="utf-8") as f:
                bula = json.load(f)

            frases = []
            for secao, textos in bula.items():
                for frase in textos:
                    frase_limpa = re.sub(r"[\n\r]+", " ", frase)
                    frase_limpa = re.sub(r"-\s+", "", frase_limpa)
                    frase_limpa = re.sub(r"\s+", " ", frase_limpa).strip()
                    frases.append(frase_limpa)

            print(f"\nProcessando {arquivo} - Total de frases: {len(frases)}")

            batch_size = 16
            dataset_anotado = []

            for i in tqdm(range(0, len(frases), batch_size), desc=f"Classificando {arquivo}"):
                batch = frases[i:i+batch_size]
                batch_filtrado = [f for f in batch if len(f) >= 15]
                if not batch_filtrado:
                    continue

                resultados = classifier(batch_filtrado, efeitos, batch_size=len(batch_filtrado))
                for frase, resultado in zip(batch_filtrado, resultados):
                    melhor_label = resultado["labels"][0]
                    score = resultado["scores"][0]

                    if score >= 0.5:
                        dataset_anotado.append({
                            "texto": frase,
                            "label": melhor_label,
                            "score": round(score, 3)
                        })

            if dataset_anotado:
                df = pd.DataFrame(dataset_anotado)
                nome_base = os.path.splitext(arquivo)[0]
                caminho_csv = os.path.join(PASTA_DATASETS, f"{nome_base}_dataset.csv")
                df.to_csv(caminho_csv, index=False, encoding="utf-8")
                print(f"Dataset criado: {caminho_csv} ({len(df)} exemplos)")
            else:
                print(f"Nenhum exemplo anotado para {arquivo}")
        
        except Exception as e:
            print(f"Erro ao processar {arquivo}: {e}")
