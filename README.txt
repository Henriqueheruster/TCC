#O que o projeto faz?

Projeto criado para fazer o pré-processamento de bulas de medicamentos da base da ANVISA em português e sua classificação com modelo BERT

#Como ele funciona?

As bulas em .PDF devem ser compactadas em .ZIP e colocadas na pasta "entrada" do projeto (caso a pasta não exista é necessario cria-lá), 
na pasta "saida_segmentada" estará os arquivos compactados .JSON ou .TXT dependendo da sua escolha.
ao executar o programa e seguir as instruções dadas ele irpa gerar um arquivos .CSV para cada bula, este arquivo será colocado na pasta datasets.

#Comando para crias os diretorios a serem usados
rode esse comando no diretorio raiz do projeto

mkdir entrada 

#Depedencias a serem instaladas

pip install -r requirements.txt #para as bibliotecas
python -m spacy download pt_core_news_lg #para o Spacy

#Rodar o projeto

python main.py







