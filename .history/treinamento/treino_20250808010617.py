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
    pipe = pipeline('text-generation', model='neuralmind/bert-base-portuguese-cased')
    for i in medicamentos:
        entrada = "As indicações desse medicamento são "+i.indicacao+" As caracteristicas farmacologica deste medicamento "+i.caracteristica_farmacologicas+" Este medicamento é contraindicado para "+i.contraindicacao+" As advertencias e precausões deste medicamento são "+i.advertencia_precaucoes+"As interações medicamentosas que podem ocorrer "+i.interacao_medicamentosa+" A posologia do medicamento é "+i.posologia+" As reações adversas deste medicamento são "+i.reacoes_adversas+" Se tomar uma dose maior da recomendada pode ocorrer o seguinte "+i.superdose
        resposta = pipe("Qual os colaterais do seguinte medicamento "+entrada)
        print(resposta)
    # Carregar os rótulos
    try:
        with open("rotulos.json", encoding="utf-8") as f:
            efeitos = json.load(f)
    except Exception as e:
        print(f"Erro ao carregar rotulos.json: {e}")
        return

