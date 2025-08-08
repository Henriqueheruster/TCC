import os
import json
import zipfile
import re
import pandas as pd
import torch
from tqdm import tqdm
from transformers import pipeline
from transformers import AutoTokenizer, BertForSequenceClassification

PASTA_SEGMENTADA = "saida_segmentada"
PASTA_DATASETS = "datasets"
ARQUIVO_ZIP = "saida_segmentada/segmentados.zip"
os.makedirs(PASTA_DATASETS, exist_ok=True)

def limpar_frases(frases):
    frases_limpa = []
    for frase in frases:
        frase_limpa = re.sub(r"[\n\r]+", " ", frase)
        frase_limpa = re.sub(r"-\s+", "", frase_limpa)
        frase_limpa = re.sub(r"\s+", " ", frase_limpa).strip()        
        frases_limpa.append(frase_limpa)
    return frases_limpa


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
        with open("treinamento/rotulos.json", encoding="utf-8") as f:
            rotulos = json.load(f)
            id2label = {i: label for i, label in enumerate(rotulos)}
            label2id = {label: i for i, label in id2label.items()}
    except Exception as e:
        print(f"Erro ao carregar rotulos.json: {e}")
        return

    try:
        tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-uncased")
        model = BertForSequenceClassification.from_pretrained(
            "google-bert/bert-base-uncased",
            num_labels=len(rotulos),
            problem_type="multi_label_classification"
        )
        model.config.id2label = id2label
        model.config.label2id = label2id
        model.eval()
    except Exception as e:
        print(f"Erro ao carregar modelo BERT: {e}")
        return
    
    arquivos_process = [arq for arq in os.listdir(PASTA_SEGMENTADA) if arq.endswith((".json", ".txt"))]

    for arquivo in arquivos_process:
        caminho = os.path.join(PASTA_SEGMENTADA, arquivo)
        try:

            if arquivo.lower().endswith(".json"):
                with open(caminho, encoding="utf-8") as f:
                    bula = json.load(f)

                frases = []
                for secao, textos in bula.items():
                    frases.extend(textos)
                frases = limpar_frases(frases)
                        
            elif arquivo.lower().endswith(".txt"):
                with open(caminho, encoding="utf-8") as f:
                    texto = f.read()
                frases = re.split(r'[.!?]', texto)
                frases = limpar_frases(frases)
                
            print(f"\nProcessando {arquivo} - Total de frases: {len(frases)}")

            batch_size = 16
            dataset_anotado = []

            for i in tqdm(range(0, len(frases), batch_size), desc=f"Classificando {arquivo}"):
                batch = frases[i:i+batch_size]
                batch_filtrado = batch
                if not batch_filtrado:
                    continue

                inputs = tokenizer(batch_filtrado, padding=True, truncation=True, return_tensors="pt")
                with torch.no_grad():
                    logits = model(**inputs).logits
                    probs = torch.sigmoid(logits)

                for j, prob in enumerate(probs):
                    rótulos_ativos = [id2label[idx] for idx, p in enumerate(prob) if p > 0.5]
                    if rótulos_ativos:
                        dataset_anotado.append({
                            "texto": batch_filtrado[j],
                            "labels": ", ".join(rótulos_ativos),
                            "scores": ", ".join([str(round(float(prob[idx]), 3)) for idx in range(len(prob)) if prob[idx] > 0.5])
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

