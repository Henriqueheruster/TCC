import json
import os
import re
import zipfile

import pandas as pd
from tqdm import tqdm
from transformers import pipeline

PASTA_SEGMENTADA = "saida_segmentada"
PASTA_DATASETS = "datasets"
os.makedirs(PASTA_DATASETS, exist_ok=True)


def classificar_efeitos_bulas(medicamentos):
    
    # Carregar os rótulos
    try:
        with open("rotulos.json", encoding="utf-8") as f:
            efeitos = json.load(f)
    except Exception as e:
        print(f"Erro ao carregar rotulos.json: {e}")
        return

