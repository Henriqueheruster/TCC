import re

def vassoura(texto):    
    pattern = r"^.+\s+\d+\s*$"
    texto = re.sub(pattern, "", texto, flags=re.MULTILINE)
    
    pattern_central = r".*Bula do Profissional de Saúde.*"
    texto = re.sub(pattern_central, "", texto, flags=re.MULTILINE | re.IGNORECASE)
    
    pattern_linhas_brancas = r"^[ \t\v\f]*$\r?\n?"
    texto = re.sub(pattern_linhas_brancas, "", texto, flags=re.MULTILINE | re.IGNORECASE)
    
    pattern_romano = r"^\s*(M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))\.?\s+"
    texto = re.sub(pattern_romano, "", texto, flags=re.IGNORECASE)

    return texto
