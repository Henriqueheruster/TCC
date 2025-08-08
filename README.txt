#O que o projeto faz?

Projeto criado para fazer o pré-processamento de bulas de medicmanetos da base da ANVISA em português e classificação com modelo joeddav/xlm-roberta-large-xnli

#Como ele funciona?

As bulas em .PDF devem ser compactadas e colocadas na pasta "entrada" do projeto, na pasta saida_segmentada estará os arquivos compactados JSON segmentados que passaram ao modelo para serem classficiados

#Depedencias a serem instaladas

mkdir entrada

pip install -r requirements.txt

python -m spacy download pt_core_news_lg

#Rodar o projeto

python main.py





