import json
import os
import re
import zipfile

from PyPDF2 import PdfReader

from modelo.modelos import MedicamentoInf
from treinamento.treino import classificar_efeitos_bulas
from utils import vassoura

PASTA_ENTRADA = "entrada"
PASTA_SAIDA = "saida"
PASTA_TEMP = os.path.join(PASTA_ENTRADA, "temp")
os.makedirs(PASTA_TEMP, exist_ok=True)


def processar_pdf(caminho_pdf):
    nome_arquivo = os.path.splitext(os.path.basename(caminho_pdf))[0]
    caminho_txt = os.path.join(PASTA_SAIDA, nome_arquivo + ".txt")

    try:
        with open(caminho_txt, "w", encoding="utf-8") as writer:
            reader = PdfReader(caminho_pdf)
            for pagina in reader.pages:
                texto = pagina.extract_text()
                if texto:
                    texto_limpo = vassoura(texto)
                    writer.write(texto_limpo + "\n")
        print(f" Processado: {caminho_pdf}")
    except Exception as e:
        print(f" Erro em {caminho_pdf}: {e}")

def extrair_e_processar_zip(caminho_zip):
    with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
        zip_ref.extractall("entrada/temp")
        for nome_arquivo in zip_ref.namelist():
            if nome_arquivo.lower().endswith(".pdf"):
                caminho_pdf = os.path.join("entrada/temp", nome_arquivo)
                processar_pdf(caminho_pdf)

def buscar_arquivos():
    for raiz, _, arquivos in os.walk(PASTA_ENTRADA):
        for arquivo in arquivos:
            caminho = os.path.join(raiz, arquivo)
            if arquivo.lower().endswith(".pdf"):
                processar_pdf(caminho)
            elif arquivo.lower().endswith(".zip"):
                extrair_e_processar_zip(caminho)
                
def extrair_medicamentos():
    secoes_permitidas = [
        "INDICAÇÕES",
        "CARACTERÍSTICAS FARMACOLÓGICAS",
        "CONTRAINDICAÇÕES",
        "ADVERTÊNCIAS E PRECAUÇÕES",
        "INTERAÇÕES MEDICAMENTOSAS",
        "POSOLOGIA E MODO DE USAR",
        "REAÇÕES ADVERSAS",
        "SUPERDOSE"
    ]

    secoes_parada = [
        "RESULTADOS DE EFICÁCIA",
        "CUIDADOS DE ARMAZENAMENTO DO MEDICAMENTO",
        "Em caso de intoxicação ligue para 0800 722 6001, se você precisar de mais orientações",
        "CONTRAINDICAÇÕES",
        "ADVERTÊNCIAS E PRECAUÇÕES",
        "INTERAÇÕES MEDICAMENTOSAS",
        "POSOLOGIA E MODO DE USAR",
        "REAÇÕES ADVERSAS",
        "SUPERDOSE",
        "DIZERES LEGAIS"
    ]

    medicamentos = []

    for arquivo in os.listdir(PASTA_SAIDA):
        if not arquivo.lower().endswith(".txt"):
            continue

        caminho_txt = os.path.join(PASTA_SAIDA, arquivo)
        with open(caminho_txt, "r", encoding="utf-8") as f:
            texto = f.read()

        secoes_extraidas = {}

        pattern = (
            r"(\n|^|\s)(\d{0,2}\.?\s?(" +
            "|".join(re.escape(s) for s in secoes_permitidas) +
            r"))\s*(.*?)(?=\n\d{0,2}\.?\s?(" +
            "|".join(re.escape(s) for s in secoes_parada) +
            r"))"
        )

        regex_obj = re.compile(pattern, re.DOTALL)
        matches = regex_obj.findall(texto)

        for match in matches:
            titulo = match[1].strip().upper()
            conteudo = match[3].strip()
            if titulo in secoes_permitidas and titulo not in secoes_extraidas:
                secoes_extraidas[titulo] = conteudo

        medicamento = MedicamentoInf()
        medicamento.indicacao = secoes_extraidas.get("INDICAÇÕES", "")
        medicamento.caracteristica_farmacologicas = secoes_extraidas.get("CARACTERÍSTICAS FARMACOLÓGICAS", "")
        medicamento.contraindicacao = secoes_extraidas.get("CONTRAINDICAÇÕES", "")
        medicamento.advertencia_precaucoes = secoes_extraidas.get("ADVERTÊNCIAS E PRECAUÇÕES", "")
        medicamento.interacao_medicamentosa = secoes_extraidas.get("INTERAÇÕES MEDICAMENTOSAS", "")
        medicamento.posologia = secoes_extraidas.get("POSOLOGIA E MODO DE USAR", "")
        medicamento.reacoes_adversas = secoes_extraidas.get("REAÇÕES ADVERSAS", "")
        medicamento.superdose = secoes_extraidas.get("SUPERDOSE", "")

        medicamentos.append(medicamento)

    return medicamentos



if __name__ == "__main__":
    print("comecou")
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    os.makedirs(PASTA_TEMP, exist_ok=True)
    print("criou diretorios")
    buscar_arquivos()
    print("buscou arquivos")
    print("Conversão concluída.\nExtraindo informações dos medicamentos...")
    medicamentos_extraidos = extrair_medicamentos()
    print("Processo finalizado.")

    print("Deseja iniciar o processo de classificação dos efeitos colaterais?",end="")
    resposta = input().strip().lower()
    if resposta == "s":
        classificar_efeitos_bulas(medicamentos_extraidos)
        print("Processo de classificação finalizada")
    else:
        print("Erro na classificação!")

    
