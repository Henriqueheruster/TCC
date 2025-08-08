#O que o projeto faz?

Projeto criado para fazer o pré-processamento de bulas de medicamentos da base da ANVISA em português, utilizando Expressões regualres e a Biblioteca Spacy

#Como ele funciona?

As bulas em .PDF devem ser compactadas em .ZIP e colocadas na pasta "entrada" do projeto (caso a pasta não exista é necessario cria-lá), 
na pasta saida_segmentada (caso a pasta não exista é necessario cria-lá) estará os arquivos compactados .JSON ou .TXT dependendo da sua escolha.

#Depedencias a serem instaladas

python -m spacy download pt_core_news_lg

#Rodar o projeto

python main.py







